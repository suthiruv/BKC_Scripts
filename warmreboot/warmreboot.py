from asyncore import read
import os
import argparse
import pickle
import subprocess
 
SERVICE_FILE_PATH = "/etc/systemd/system/"
SERVICE_FILE = 'run-reboot.service'
CUR_DIR = os.path.curdir
REBOOT_LOGGER_PKLFILE = 'current_reboot_count.pkl'
COMMAND = "reboot"

def server_reboot():
    os.system(COMMAND)

def create_reboot_service():
    ser_str= '''[Unit]
Description=Startup Script

[Service]
User=root
Type=simple
Restart=always
ExecStart={}

[Install]
WantedBy=multi-user.target'''.format(os.path.dirname(os.path.abspath(__file__)))

    with open(os.path.join(SERVICE_FILE_PATH, SERVICE_FILE), 'w') as f:
        f.write(ser_str)
        f.close()

    subprocess.call(['chmod', '0777', os.path.join(SERVICE_FILE_PATH, SERVICE_FILE)])
    subprocess.run(('systemctl enable' + ' ' + SERVICE_FILE), shell=True, check=True)


def write_pkl_file(reboot_data):
    with open(os.path.join(CUR_DIR, REBOOT_LOGGER_PKLFILE), 'wb') as f:
        pickle.dump(reboot_data, f)
        f.close()

def read_pkl_file():
    with open(os.path.join(CUR_DIR, REBOOT_LOGGER_PKLFILE), 'rb') as f:
        reboot_params = pickle.load(f)
        f.close()
    return reboot_params

if __name__ == "__main__":

    try:
        reboot_params = read_pkl_file()
    except FileNotFoundError as e:
        print ("-I- Pickle file not found as test is running its first loop")
        parser = argparse.ArgumentParser(description=('Warm Reboot Test and check the '))
        parser.add_argument('--reboot_loop', type=int, required=True, help=('This param to mention no of reboots') )
        args = parser.parse_args()
        
        reboot_data = {'reboot_count' : 1, 'total_reboot' : args.reboot_loop }
    
        create_reboot_service()
    
        write_pkl_file(reboot_data) # creates reboot file and writes count as 1

        if args.reboot_loop != 0:
          server_reboot()
    else:
        if (reboot_params['reboot_count'] <= reboot_params['total_reboot']):
            reboot_params['reboot_count'] = reboot_params['reboot_count'] + 1
            write_pkl_file(reboot_params)
            server_reboot()
        else:
            # delete pkl file
            # delete service file
            # disable auto run
            subprocess.run(('systemctl disable' + ' ' + SERVICE_FILE), shell=True, check=True)
            os.remove(os.path.join(CUR_DIR, REBOOT_LOGGER_PKLFILE))
            os.remove(os.path.join(SERVICE_FILE_PATH, SERVICE_FILE))

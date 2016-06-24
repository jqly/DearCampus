import requests
import json
from threading import Thread, Lock

import sys

from TaskManager.TaskManager import task_partition
from time import sleep

LoginUrl = 'http://172.20.13.100/cgi-bin/do_login'
PassportFile = 'C:/Users/jerry/PycharmProjects/DearCampus/LovelyNet/res/passport.txt'

lock = Lock()
Done = False


def connector(passport: list):
    global Done

    form_data = dict(username='', password='')
    for p in passport:
        if Done:
            return
        form_data['username'], form_data['password'] = p['username'], p['password']
        try:
            r = requests.post(LoginUrl, form_data).text
        except:
            continue
        if r == 'ip_exist_error' or r.isdigit():
            with lock:
                Done = True
            return


if __name__ == '__main__':
    with open(PassportFile, 'r') as file:
        passports = json.load(file)
    partitions = task_partition(0, len(passports), 20)
    threads = [Thread(target=connector, args=(passports[p[0]:p[1]],)) for p in partitions]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    if Done:
        print('Happy browsing!')
    else:
        print('Passports are exhausted. Login failed.')
    print('\nExit in 3 seconds', end='')
    for i in range(3):
        print('. ', end='')
        sys.stdout.flush()
        sleep(1)

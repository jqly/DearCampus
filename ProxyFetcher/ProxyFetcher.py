import threading
import json
from TaskManager.TaskManager import task_partition

import requests
from threading import Thread

ProxyFile = 'res/proxy.txt'
RawProxyFile = 'res/raw_proxies.txt'
GProxies = []
lock = threading.Lock()


def clean_proxies(proxies: list):
    test_url = 'http://www.baidu.com/'

    valid_proxies = []
    for proxy in proxies:
        try:
            r = requests.get(test_url, proxies={'http': proxy}, timeout=5).text
            if len(r) > 90000 and r[890] == '度':
                print('Add %s' % proxy)
                valid_proxies.append(proxy)
        except requests.exceptions.RequestException:
            pass
            # print(str(sys.exc_info()))
    global GProxies
    with lock:
        GProxies += valid_proxies


def parse_proxies() -> list:
    with open(RawProxyFile, 'r') as file:
        return json.load(file)


def fetch_proxies():
    raw_proxies = parse_proxies()
    partitions = task_partition(0, len(raw_proxies), 100)
    print(len(raw_proxies), len(partitions))
    threads = [Thread(target=clean_proxies, args=(raw_proxies[p[0]:p[1]],)) for p in partitions]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    with open(ProxyFile, 'w') as f:
        json.dump(list(set(GProxies)), f)
    return GProxies


if __name__ == '__main__':
    proxies = fetch_proxies()
    print(proxies)

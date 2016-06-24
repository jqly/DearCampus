import time
from threading import active_count


def task_partition(task_begin: int, task_end: int, ideal_total_threads: int) -> list:
    total_tasks = task_end - task_begin
    page_per_thread = total_tasks // ideal_total_threads + 1
    partition = []
    for i in range(ideal_total_threads):
        s = i * page_per_thread + task_begin
        e = min(task_end, (i + 1) * page_per_thread + task_begin)
        if s < e:
            partition.append((s, e))
    return partition


def miscellaneous(lock, on_run):
    if active_count() > 30:
        timeout = 15
        sleep = 1.5
    elif active_count() > 15:
        timeout = 10
        sleep = 1
    elif active_count() > 5:
        timeout = 6
        sleep = 0.5
    else:
        timeout = 4
        sleep = 0
    with lock:
        on_run['timeout'] = timeout
        on_run['sleep'] = sleep


def task_manager(total_threads: int, lock, thread_status: dict, on_run: dict):
    while True:
        total_status = 0.0
        s = '\n\n'
        with lock:
            status = [(i, thread_status.get(i, 0)) for i in range(total_threads)]
        current_threads = 0
        for i in range(total_threads):
            total_status += status[i][1]
            if i % 4 != 3:
                s += 'Thread %-3d status: %05.2f%%\t' % (status[i][0], 100 * status[i][1])
            else:
                s += 'Thread %-3d status: %05.2f%%\n' % (status[i][0], 100 * status[i][1])
            if status[i][1] >= 0.99:
                current_threads += 1
        total_status /= total_threads
        if total_status > 0.9999:
            total_status = 1
        print(s)
        print('Status: %.2f%%' % (total_status * 100))
        if current_threads == total_threads:
            break
        miscellaneous(lock, on_run)
        time.sleep(5)

    print('Done!')


if __name__ == '__main__':
    lis = task_partition(task_begin=1, task_end=10, ideal_total_threads=20)
    print(len(lis), lis)

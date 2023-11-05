import os
from multiprocessing import Process, Pool
from auto_tmin import *

if __name__ == '__main__':

    with open('triage-output.txt', 'r') as f:
        data = f.read()
        crashes = list(data.split('\n'))

    p_list = []

    for crash in crashes:
        try:
            crash = json.loads(crash)
            p = Process(target=tmin, args=(crash,))
            p.start()
            print('starting process')
            print('crash:', crash['id'])
            p_list.append(p)
        except:
            continue

    for p in p_list:
        p.join()

    for x in process_result:
        print(f"Crash {x['id']}: {x['res']}")
    



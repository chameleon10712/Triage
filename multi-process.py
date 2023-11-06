import os
from multiprocessing import Process, Pipe
from auto_tmin import *

if __name__ == '__main__':

    with open('triage-output.txt', 'r') as f:
        data = f.read()
        crashes = list(data.split('\n'))

    p_list = []
    conn_list = []
    res = []

    for crash in crashes:
        try:
            crash = json.loads(crash)
            # parent_conn, child_conn = Pipe()

            p = Process(target=app, args=(crash,))
            p.start()
            print('starting process')
            print('crash:', crash['id'])
            p_list.append(p)
            # conn = (parent_conn, child_conn)
            # conn_list.append(conn)

        except:
            continue

    for idx, p in enumerate(p_list):
        # res.append(conn_list[idx][0].recv())
        p.join()

    # for r in res:
    #     print(r)



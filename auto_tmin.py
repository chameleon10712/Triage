import os
import json
import subprocess
from config import *
from utils import *

TIMEOUT = 720

process_result = []

def tmin(crash, conn=None):

    id_ = crash['id']
    if not os.path.exists(f'./pocs/poc_{id_}'):
        print(f'./pocs/poc_{id_} does not exist')
        x = {'id': id_, 'res': f'./pocs/poc_{id_} does not exist'}
        process_result.append(x)
        return
    elif crash['ASAN'] == []:
        print(f'Crash: {id_} does not have ASAN report')
        x = {'id': id_, 'res': 'does not have ASAN report'}
        process_result.append(x)
        return

    if 'must' in crash:
        must = ' '.join(crash['must'])
    else:
        must = ' '.join(crash['params'].split()[:-1])

    if '#' in must:
        must.replace('#', '\#')
        print(f'Crash: {id_} replace # with \#')
        print('must', must)

    # afl-tmin -i ./pocs/poc_29 -o poc_min_29  /home/oceane/libsixel/build_afl/bin/img2sixel -d jajuni -e @@
    cmd = f"afl-tmin -i ./pocs/poc_{id_} -o ./pocs/poc_min_{id_} -- {afl_target} {must} @@"
    print('cmd', cmd)

    cmd = cmd.split()
    result = subprocess.run(cmd, timeout=TIMEOUT)
    # print(result)
    # result = result.stderr.decode("utf-8").splitlines()
    if result.returncode != 0:
        print(f'Crash: {id_} returncode != 0')
        x = {'id': id_, 'res': 'returncode !=0'}
        process_result.append(x)
        return

    return


def check_min(crash):
    id_ = crash['id']
    if 'must' in crash:
        must = ' '.join(crash['must'])
    else:
        must = ' '.join(crash['params'].split()[:-1])

    if not os.path.exists(f'./pocs/poc_min_{id_}'):
        print(f'./pocs/poc_min_{id_} does not exist')
        return

    filesize = os.path.getsize(f'./pocs/poc_min_{id_}')
    if filesize == 0:
        print('WARNING: Down to zero bytes - check the command line and mem limit!')
        x = {'id': id_, 'res': 'Down to zero bytes'}
        process_result.append(x)
        return

    # check poc_Min
    cmd = f"{target} {must} ./pocs/poc_min_{id_}"
    print(f'Crash: {id_} checking poc_min ...\n cmd: ', cmd)
    cmd = cmd.split()
    result = subprocess.run(cmd, capture_output=True, timeout=TIMEOUT)
    returncode = result.returncode
    print('returncode', returncode)
    
    if returncode == 255:
        print(result.stderr.decode("utf-8"))

    # result is None if capture_output==False
    if result.stderr is not None:
        result = result.stderr.decode("utf-8").splitlines()
    elif result.stdout is not None:
        result = result.stdout.decode("utf-8").splitlines()
    else:
        print(f'Crash: {id_} poc_min result is None')
        x = {'id': id_, 'res': 'result is None'}
        process_result.append(x)
        return

    res = parse(result)
    file_name = res[0]
    func_name = res[2]
    if len(res) > 3:
        shadow_bytes = res[5]

    if returncode==crash['returncode'] and file_name==crash['ans']['file'] and func_name==crash['ans']['func']:
        if shadow_bytes==crash['shadow_bytes']:
            print(f'Crash: {id_} contains shadow_bytes')

        print(f'[OK] Crash: {id_} success')
        x = {'id': id_, 'res': 'success'}
        process_result.append(x)

    return


def app(crash, conn=None):
    tmin(crash)
    check_min(crash)
    return


def test():
    with open('triage-output.txt', 'r') as f:
        data = f.read()
        crashes = list(data.split('\n'))

    #3: id:00050
    # crash = crashes[0]
    for crash in crashes:
        try:
            crash = json.loads(crash)
        except:
            continue
        tmin(crash)
        check_min(crash)


if __name__ == '__main__':
    test()


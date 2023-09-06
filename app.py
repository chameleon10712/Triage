import os
import glob
import subprocess
import json
import shutil
import getopt, sys
from config import *

crashes = []
triage_crashes = []


def arg_minimize(index):
    parameters = ['-'+e for e in crashes[index]['params'].split('-') if e]
    # print('parameters', parameters,'\n\n')

    n = len(parameters)
    must = []

    for i in range(n):
        last = parameters.pop()
        s = ''.join(parameters+must)
        _list = s.split()

        poc_path = pocs_dir + '/' + crashes[index]['poc']
        result = run_cmd(_list, poc_path)
        res = parse(result)
        # print(file_name, line_no, func_name)
        file_name = res[0]
        line_no = res[1]
        func_name = res[2]

        if file_name==crashes[index]['ans']['file'] and func_name==crashes[index]['ans']['func']:
            pass
        # print('pass')
    else:
        # print('failed, must add', last, '\n')
        must.append(last)

    crashes[index]['must'] = must


def parse(result):
    report = ''
    for line in result:
        if 'SUMMARY' in line:
            report = line
            break

    if report == '':
        return '', '', ''

    # print(report)
    info = report.split()
    func_name = info[-1] 
    file_name = info[-3].split('/')[-1]
    line_no = file_name.split(':')[-1]
    file_name = file_name.split(':')[0]
    # print(file_name, line_no, func_name)

    if file_name == 'AddressSanitizer':
        print("file_name == 'AddressSanitizer'")
        for line in result:
            if 'ERROR' in line:
                report = line
                break
        info = report.split()
        func_name=file_name=line_no=None

    return [file_name, line_no, func_name, info]


def run_cmd(params, poc_path):
    cmd = []
    cmd.append(target)
    # shutil.copyfile(poc, '/home/oceane/fuzz_test/Triage/poc')

    for idx in range(len(params)):
        if '@@' in params[idx]:
            # params[idx] = '/home/oceane/fuzz_test/Triage/poc'
            params[idx] = poc_path

    cmd += params
    # print('cmd', cmd)
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=4)
        # print(result.stderr.decode("utf-8"))
        result = result.stderr.decode("utf-8").splitlines()
    except:
        result = []

    return result


def base(i):

    crashes[i]['id'] = str(i)
    poc_path = pocs_dir + '/' + crashes[i]['poc']
    local_path = './pocs/poc_'+ str(i)
    shutil.copyfile(poc_path, local_path)
    result = run_cmd(crashes[i]['params'].split(), local_path)

    crashes[i]['ASAN'] = result
    # crashes[i]['ans']['file'], crashes[i]['ans']['line_no'], crashes[i]['ans']['func'], crashes[i]['ans']['info'] = parse(result)
    res = parse(result)
    crashes[i]['ans']['file'] = res[0]
    crashes[i]['ans']['line_no'] = res[1]
    crashes[i]['ans']['func'] = res[2]
    if len(res) > 3:
        crashes[i]['ans']['info'] = ' '.join(res[3])


def get_params(entry):
    path = params_dir + entry
    result = subprocess.run(['cat', path], capture_output=True).stdout.decode("utf-8")
    params = result.split()
    params.pop(0)
    for idx in range(len(params)):
        if '.cur_input' in params[idx]:
            params[idx] = '@@'
    # print('params', params)
    return ' '.join(params)


def init():
    print('Check crashes dir ...')
    result = subprocess.run(['ls', pocs_dir], capture_output=True)
    result = result.stdout.decode("utf-8")
    entries = result.split('\n')

    for entry in entries:
        if entry.startswith('id:'):
            params = get_params(entry)
            crashes.append({'poc': entry,
                'params': params,
                'ASAN': '',
                'ans': {'file': '', 'line_no': '', 'func': '', 'info': ''}
            })


def triage(crash):
    # print(crash)
    if triage_crashes == []:
        # print('index', i)
            return

    for each in triage_crashes:
        if each['ans']['file'] == crash['ans']['file'] and each['ans']['func'] == crash['ans']['func']:
            pass
        else:
            print('append', crashes[i])
            triage_crashes.append(crash) 


def app(start=0, end=None):
    print('Searching crash directories...')
    max_len = len(crashes)
    # print(crashes)

    if end is None or end > max_len:
        end = max_len

    print('Running start from id: '+ str(start) + ' to '+ str(end))
    # arg minimize
    #prefix = "id-" + str(start)+"-to-"+str(end)+"-"
    prefix = ""
    with open(prefix + 'output.txt', 'w') as f:
        # f.write('[')
            for i in range(start, end):    
                print('id: ', i)
                base(i)
                # arg_minimize(i)
                # print(crashes[i])
                # triage(crashes[i])
                f.write(json.dumps(crashes[i]))
                f.write('\n')
                # f.write(',\n')
            # f.write(']')

    # print('triage', triage_crashes)

def crash_print(_id):
    print('Running id:',_id, '...')
    base(_id)
    print(crashes[_id]['params'])
    for line in crashes[_id]['ASAN']:
        print(line)


if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "s:e:i:", ["start=", "end=", "id="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err)  # will print something like "option -a not recognized"
        # usage()
        sys.exit(2)

    start = -1
    end = -1
    _id = -1
    # print(opts)
    for o, a in opts:
        if o in ("-i", "--id"):
            _id = int(a)    
        elif o in ("-s", "--start"):
            start = int(a)
        elif o in ("-e", "--end"):
            end = int(a)
        else:
            assert False, "unhandled option"

    init() # Find all crashes in dir, append to `crashes[]`
    if len(sys.argv) == 1:
        app()
    elif _id != -1:
        crash_print(_id)
    elif start != -1 or end !=-1:
        app(start, end)




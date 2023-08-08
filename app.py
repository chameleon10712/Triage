import os
import glob
import subprocess
import json
import shutil


pocs_dir = '/home/oceane/fuzz_test/SQ-fuzz-fast-splice2/tiffcrop_output_d/crashes'
params_dir = '/home/oceane/fuzz_test/SQ-fuzz-fast-splice2/tiffcrop_output_d/queue_info/crashes/'
target = '/home/oceane/fuzz_test/tiff-4.4.0/build_asan/bin/tiffcrop'
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
        # elif 'error' in line:
        #     report = line
        #     break

    if report == '':
        return '', '', ''

    # print(report)
    info = report.split()
    func_name = info[-1] 
    file_name = info[-3].split('/')[-1]
    line_no = file_name.split(':')[-1]
    file_name = file_name.split(':')[0]
    # print(file_name, line_no, func_name)
    return [file_name, line_no, func_name, info]


def run_cmd(params, poc):
    cmd = []
    cmd.append(target)
    shutil.copyfile(poc, '/home/oceane/fuzz_test/Triage/poc')

    for idx in range(len(params)):
        if '@@' in params[idx]:
            params[idx] = '/home/oceane/fuzz_test/Triage/poc'

    cmd += params
    # print('cmd', cmd)
    result = subprocess.run(cmd, capture_output=True)
    # print(result.stderr.decode("utf-8"))
    result = result.stderr.decode("utf-8").splitlines()
    return result


def base(i):

    poc_path = pocs_dir + '/' + crashes[i]['poc']
    result = run_cmd(crashes[i]['params'].split(), poc_path)
    crashes[i]['ASAN'] = result
    # crashes[i]['ans']['file'], crashes[i]['ans']['line_no'], crashes[i]['ans']['func'], crashes[i]['ans']['info'] = parse(result)
    res = parse(result)
    crashes[i]['ans']['file'] = res[0]
    crashes[i]['ans']['line_no'] = res[1]
    crashes[i]['ans']['func'] = res[2]
    if len(res) > 3:
        crashes[i]['ans']['info'] = ' '.join(res[3])

    # _list = [target]
    # params = crashes[i]['params'].split()
    # _list += params
    # poc_path = pocs_dir + '/' + crashes[i]['poc']
    # _list.append(poc_path)
    # result = subprocess.run(_list, capture_output=True)
    # print(result.stderr.decode("utf-8"))
    # result = result.stderr.decode("utf-8").splitlines()
    # crashes[i]['ASAN'] = result
    # return result


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


def list_crashes():

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

    # for crash in crashes:
    #     print(crash)

def triage(crash):
    # print(crash)
    if triage_crashes == []:
        # print('index', i)
        print('append', crashes[i])
        triage_crashes.append(crashes[i])

    for each in triage_crashes:
        if each['ans']['file'] == crash['ans']['file'] and each['ans']['func'] == crash['ans']['func']:
            pass
        else:
            print('append', crashes[i])
            triage_crashes.append(crash) 


if __name__ == '__main__':
    list_crashes()

    # arg minimize
    with open('output.txt', 'w') as f:
        # f.write('[')
        for i in range(len(crashes)):    
            base(i)
            # arg_minimize(i)
            # print(crashes[i])
            # triage(crashes[i])
            f.write(json.dumps(crashes[i]))
            f.write('\n')
            # f.write(',\n')
        # f.write(']')

    # print('triage', triage_crashes)



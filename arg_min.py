import json
import subprocess
from config import *

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
    error_type = info[2]
    print('info', info)
    print('error type', error_type)
    # print('parse', file_name, line_no, func_name)

    if file_name == 'AddressSanitizer':
        print("file_name == 'AddressSanitizer'")
        for line in result:
            if 'ERROR' in line:
                report = line
                break
        info = report.split()
        func_name=file_name=line_no=None

    return [file_name, line_no, func_name, info, error_type]

def run_cmd(params, poc):
    cmd = []
    cmd.append(target)
    cmd += params
    cmd.append(poc)
    print(' '.join(cmd))
    result = subprocess.run(cmd, capture_output=True, timeout=4)
    print('returncode', result.returncode)
    returncode = result.returncode
    # print(result.stderr.decode("utf-8"))
    result = result.stderr.decode("utf-8").splitlines()
    return result, returncode

def arg_minimize(crash):
    parameters = ['-'+e for e in crash['params'].split('-') if e]
    # print('parameters', parameters,'\n\n')

    n = len(parameters)
    must = []

    for i in range(n):
        last = parameters.pop()
        s = ''.join(parameters+must)
        _list = s.split()

        poc_path = pocs_dir + '/' + crash['poc']
        result, returncode = run_cmd(_list, poc_path)
        res = parse(result)
        # print(file_name, line_no, func_name)
        file_name = res[0]
        line_no = res[1]
        func_name = res[2]

        if len(res) > 4:
            error_type = res[4]
        else:
            error_type = None

        # print('original err', crash['ans']['err'])
        # print('ori returncode', crash['returncode'])
        # print('return code', returncode)
        if returncode==crash['returncode'] and file_name==crash['ans']['file'] and func_name==crash['ans']['func'] and error_type==crash['ans']['err']:
            pass
        # print('pass')
        else:
            # print('failed, must add', last, '\n')
            must.append(last)

    return must


def app():
    with open('output.txt', 'r') as f:
        data = f.read()
        crashes = list(data.split('\n'))

    x = crashes[29]
    print(x)
    print('crash type', x)
    x = json.loads(x)
    must = arg_minimize(x) 
    print('must', must)


app()


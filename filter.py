import json
import subprocess

triage_list = []
pocs_dir = '/home/oceane/fuzz_test/Yuan-fuzz-cg/fuzz_output_d/crashes'
target = '/home/oceane/fuzz_test/new_djpeg/libjpeg-turbo/build_asan_g/djpeg'

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
    return [file_name, line_no, func_name, info]

def run_cmd(params, poc):
    cmd = []
    cmd.append(target)
    cmd += params
    cmd.append(poc)
    result = subprocess.run(cmd, capture_output=True)
    # print(result.stderr.decode("utf-8"))
    result = result.stderr.decode("utf-8").splitlines()
    return result

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
        result = run_cmd(_list, poc_path)
        res = parse(result)
        # print(file_name, line_no, func_name)
        file_name = res[0]
        line_no = res[1]
        func_name = res[2]

        if file_name==crash['ans']['file'] and func_name==crash['ans']['func']:
            pass
        # print('pass')
    else:
        # print('failed, must add', last, '\n')
        must.append(last)
    
    return must


def triage(crash):
    if triage_list == []:
        triage_list.append(crash)
        # print(crash)
        return

    flag = False

    for item in triage_list:
        # print('\nlist', item['ans']['file'], item['ans']['func'])
        # print('crash',  crash['ans']['file'], crash['ans']['func'])
        if item['ans']['func'] == crash['ans']['func']:
            if item['ans']['file'] == crash['ans']['file']:
                flag = True
                # print('duplicate')
                break
            else:
                # flag = True
                # print('duplicate??')
                break

    if flag is False:
        # must = arg_minimize(crash)
        # crash['must'] = must
        triage_list.append(crash)
        # print('unique')
    

with open('output.txt', 'r') as f:
    data = f.read()
    crashes = list(data.split('\n'))

# print(crashes[0])
# print(type(json.loads(crashes[0])))

for x in crashes:
    # print(x, '\n')
    if x != '':
        triage(json.loads(x))
 
for i, item in enumerate(triage_list):
    if item['ans']['file'] == '':
        print('#', i, ':', item)
    else:
        print('#', i, ':', item['ans']['file'], item['ans']['func'])


with open('triage_output.txt', 'w') as f:
    for i, item in enumerate(triage_list):
        f.write(json.dumps(item))
        f.write('\n')
    



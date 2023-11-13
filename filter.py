import json
import subprocess
import getopt, sys
from config import *
from utils import *
from multiprocessing import Process, Queue

triage_list = []
prefix = ""
p_list = []
q_list = []


def run_cmd(params, poc):
    cmd = []
    cmd.append(target)
    cmd += params
    cmd.append(poc)
    print(' '.join(cmd))

    try:
        result = subprocess.run(cmd, capture_output=True, timeout=4)
        print('returncode', result.returncode)
        returncode = result.returncode
        # print(result.stderr.decode("utf-8"))
        result = result.stderr.decode("utf-8").splitlines()
    except:
        print('except')
        result = []
        returncode = None

    return result, returncode

def arg_minimize(crash, q=None):
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
        if returncode==crash['returncode'] and file_name==crash['ans']['file'] and func_name==crash['ans']['func']:
            pass
        # print('pass')
        else:
            # print('failed, must add', last, '\n')
            must.append(last)

    if q is not None:
        q.put(must)

    return must


def triage(crash):

    d = {'ids': [crash['id']]}
    crash.update(d)

    if triage_list == []:
        triage_list.append(crash)
        # print(crash)
        return

    flag = False

    i = 0
    for item in triage_list:
        '''
        print('[' + str(i) + ']')
        print('triage_list', item['ans']['file'], item['ans']['func'])
        print('crash',  crash['ans']['file'], crash['ans']['func'])
        '''

        if item['ans']['func'] == crash['ans']['func']:
            if item['ans']['file'] == crash['ans']['file']:
                flag = True
                #print('duplicate')
                item['ids'].append(crash['id'])
                break
            else:
                flag = True
                #print('duplicate??')
                break
        i = i + 1

    if flag is False:
        must = arg_minimize(crash)
        crash['must'] = must
        triage_list.append(crash)
        #print('unique')
    

def app(verbose, show_id):
    with open(prefix + 'output.txt', 'r') as f:
        data = f.read()
        crashes = list(data.split('\n'))

    for x in crashes:
        # print(x, '\n')
        if x != '' and x != []:
            triage(json.loads(x))

    # multiprocess
    # for crash in triage_list:
    #     # must = arg_minimize(crash)
    #     # crash['must'] = must
    #     q = Queue()
    #     p = Process(target=arg_minimize, args=(crash, q,))
    #     p.start()
    #     p_list.append(p)
    #     q_list.append(q)
    #
    # for i, crash in enumerate(triage_list):
    #     crash['must'] = q_list[i].get()
    #     p_list[i].join()
        

    for i, item in enumerate(triage_list):
        if item['ans']['file'] == '':
            print('#', i, ':', item)
        else:
            print('#', i, ':', item['ans']['file'], item['ans']['func'])

        if show_id:
            print(item['poc'].split(',')[0])
        if verbose:
            print('num', len(item['ids']))
            print(item['ids'])
            print(item['ans']['info'])
            print('\n')

    with open('triage-output.txt', 'w') as f:
        for i, item in enumerate(triage_list):
            f.write(json.dumps(item))
            f.write('\n')


if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], ":sv", ["show", "verbose"])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err)  # will print something like "option -a not recognized"
        # usage()
        sys.exit(2)

    verbose = False
    show_id = False

    for o, a in opts:
        if o in ("-v", "--verbose"):
            verbose = True
            show_id = True
        elif o in ("-s", "--show"):
            show_id = True

    app(verbose=verbose, show_id=show_id)



import os
import json
import getopt, sys
import shutil
import graphviz
from get_version import *
from config import *

file_name = ""
out_file = ""

def read_data():
    with open(file_name, "r") as f:
        data = f.read()
    return data.split('\n')


def get_cmd(item, path=target):
    if 'must' in item:
        params = item['must']
        poc =  item['params'].split()[-1]
        params.append(poc)
    else:
        params = item['params'].split()

    for idx in range(len(params)):
        if '@@' in params[idx]:
            params[idx] = './pocs/poc_' + item['id']

    params = ' '.join(params)
    # print(target, params)
    cmd = '$ ' + path + ' ' + params
    return cmd

def gen_version(f):
    version = get_ver()
    f.write(version)
    f.write('\n\n')

def gen_poc_context(f, item):
    cmd = 'base64 ./pocs/poc_' + item['id']
    cmd = cmd.split()
    result = subprocess.run(cmd, capture_output=True)
    # print(result.stdout.decode("utf-8"))
    text = result.stdout.decode("utf-8")
    text = text.replace('\n', '')
    text = 'echo -ne \"' + text + '\" | base64 -d > poc'
    shutil.copyfile('./pocs/poc_' + item['id'], './poc')
    f.write(text)
    f.write('\n\n')


def gen_context(f, item, path=target):
    cmd = get_cmd(item, path)
    _cmd = cmd.split('./')[0] + './poc'
    f.write(_cmd)
    f.write('\n\n')
    for line in item['ASAN']:
        f.write(line)
        f.write('\n')
    f.write('\n\n\n')


def gen_report(_id, print_normal):
    data = read_data()

    with open(out_file, "w") as f:
        for item in data:
            if item != '':
                item = json.loads(item)
                if _id == item['id']:
                    f.write('# poc\n')
                    gen_poc_context(f, item)

                    if print_normal:
                        f.write('# Normal build\n')
                        gen_context(f, item, norm_build)

                    f.write('# Build with ASAN\n')
                    gen_context(f, item, target)
                    gen_version(f)
        print("[OK] successfully generate '"+ out_file +"'")


def gen_relationship():
    data = read_data()
    d = graphviz.Digraph('relationship')
    nodes = []
    colors = ['cadetblue', 'burlywood1', 'coral', 'cornsilk3', 'darkgray', 'darkseagreen3', 'gray1']
    i = 0

    for crash in data:
        if crash == '':
            continue

        crash = json.loads(crash)['ASAN']
        if crash == [] or crash == '':
            continue

        # print(crash)
        funcs = []
        for line in crash:
            if '#' in line:
                print(line)
                func = line.split()[3]
                funcs.append(func)
                if func == 'main':
                    break

        funcs = list(reversed(funcs))
        for idx, f in enumerate(funcs):
            # print(f)
            if idx == len(funcs):
                break

            if f not in nodes:
                nodes.append(f)
                d.node(f)

            if idx !=0:
                d.edge(funcs[idx-1], f, color=colors[i])

        i = i+1
            
    with d.subgraph(name='child') as c:
        c.node('tab', rank="same", shape="box", label = '''<<TABLE>
                                                            <TR>
                                                                <TD>left</TD>
                                                                <TD>right</TD>
                                                            </TR>
                                                        </TABLE>>''')

    d.format = 'svg'
    d.render(directory='relationship-output').replace('\\', '/')

    return


def app():
    data = read_data()

    with open(out_file, "w") as f:
        for item in data:
            if item != '':
                item = json.loads(item)
                cmd = get_cmd(item)
                f.write(cmd)
                f.write('\n\n')
                f.write(item['poc'])
                f.write('\n')
                for line in item['ASAN']:
                    f.write(line)
                    # print(line)
                    f.write('\n')
                f.write('\n\n')
        print("[OK] successfully generate '"+ out_file +"'")


if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "rn:i:t:", ["normal", "id=", "triage", "relation"])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err)  # will print something like "option -a not recognized"
        # usage()
        sys.exit(2)
    
    report = False
    print_normal = False

    for o, a in opts:
        if o in ("-i", "--id"):
            report = True    

        elif o in ("-n", "--normal"):
            print_nornmal = True

        elif o in ("-t", "--triage"):
            file_name = "triage-output.txt"
            out_file = "triage-print.txt"
            app()

        elif o in ("-r", "--relation"):
            file_name = "triage-output.txt"
            gen_relationship()

        else:
            assert False, "unhandled option"

    if len(sys.argv) == 1:
        file_name = "output.txt"
        out_file = "print.txt"
        app()

    elif report:
        file_name = "output.txt"
        out_file = "report.txt"
        gen_report(a, print_normal)


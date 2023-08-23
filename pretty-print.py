import json
import getopt, sys
from get_version import *

file_name = ""
out_file = ""
target = "/home/oceane/fuzz_test/mruby_asan/build/host/bin/mruby"

def get_cmd(item):
    params = item['params'].split()
    for idx in range(len(params)):
        if '@@' in params[idx]:
            params[idx] = './pocs/poc_' + item['id']

    params = ' '.join(params)
    # print(target, params)
    cmd = '$ ' + target + ' ' + params
    return cmd


def app(_id=None):
    with open(file_name, "r") as f:
        data = f.read()
    data = data.split('\n')

    with open(out_file, "w") as f:
        for item in data:
            if item != '':
                item = json.loads(item)

                if _id is None:
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

                elif _id == item['id']:
                    cmd = get_cmd(item)
                    f.write(cmd)
                    f.write('\n\n')
                    for line in item['ASAN']:
                        f.write(line)
                        f.write('\n')
                    f.write('\n\n')
                    version = get_ver()
                    f.write(version)
                    f.write('\n\n')
        print("[OK] successfully generate '"+ out_file +"'")


if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "i:t:", ["id=", "triage"])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err)  # will print something like "option -a not recognized"
        # usage()
        sys.exit(2)

    for o, a in opts:
        if o in ("-i", "--id"):
            file_name = "output.txt"
            out_file = "report.txt"
            app(a)
            pass

        elif o in ("-t", "--triage"):
            file_name = "triage-output.txt"
            out_file = "triage-print.txt"
            app()
        else:
            assert False, "unhandled option"

    if len(sys.argv) == 1:
        file_name = "output.txt"
        out_file = "print.txt"
        app()

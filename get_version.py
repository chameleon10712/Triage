import subprocess

target_dir = '/home/oceane/fuzz_test/mruby_afl'

def run(cmd):
    cmd = cmd.split()
    lines = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode('utf-8')
    return lines

def get_compiler():
    cmd = 'gcc --version'
    gcc = run(cmd).split('\n')[0]
    cmd = 'g++ --version'
    gpp = run(cmd).split('\n')[0]
    print(gcc)
    print(gpp)

    return gcc + '\n' + gpp

def get_cpu():
    cmd = 'lscpu'
    cmd = cmd.split()
    lines = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode('utf-8')
    lines = lines.split('\n')
    for line in lines:
        if 'Model name' in line:
            cpu = line.split(':')[1].lstrip()
            print(cpu)
            break

    return cpu
    

def get_os():
    cmd = 'lsb_release -a'
    cmd = cmd.split()
    lines = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode('utf-8')
    lines = lines.split('\n')
    os = lines[2].split()
    os = ' '.join(os[1:4])
    print(os)
    return os


def get_logs():
    # cmd = 'git log --pretty="%H" -n 1'
    cmd = 'git log -n 1'
    cmd = cmd.split()
    lines = subprocess.check_output(
        cmd, stderr=subprocess.STDOUT, cwd=target_dir
    ).decode('utf-8')
    lines = lines.split('\n')[0].split()
    line = 'git '+ lines[0] +' '+ lines[1][:9]
    print(line)
    # print('git commit', lines[1:10])
    # return '$ git log --pretty="%H" -n 1\n' + lines[1:10] + '\n'
    return line

def get_ver():
    log = get_logs()
    compiler = get_compiler()
    os = get_os()
    cpu = get_cpu()
    return '\n'.join([log, compiler, os, cpu])

if __name__ == '__main__':
    v = get_ver()
    # print('\n\n\n')
    # print(v)

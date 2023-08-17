import subprocess
import os

'''
cmd = 'ls -al'
cmd = cmd.split()
subprocess.run(cmd)
'''

names = [name for name in os.listdir(".") if os.path.isdir(name)]

for name in names:
   cmd = 'ls ' + name + '/crashes'
   print(cmd)
   cmd = cmd.split()
   result = subprocess.run(cmd, capture_output=True)
   print(result.stdout.decode("utf-8"))
   print('\n')

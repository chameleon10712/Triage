import json
import getopt, sys
from get_version import *
from config import *

file_name = ""
out_file = ""


def read_data():
	with open(file_name, "r") as f:
		data = f.read()
	return data.split('\n')


def get_cmd(item, path=target):
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


def gen_context(f, item, path=target):
	cmd = get_cmd(item, path)
	f.write(cmd)
	f.write('\n\n')
	for line in item['ASAN']:
		f.write(line)
		f.write('\n')
	f.write('\n\n\n')


def gen_report(_id):

	data = read_data()
	with open(out_file, "w") as f:
		for item in data:
			if item != '':
				item = json.loads(item)
				if _id == item['id']:
					f.write('# Normal build\n')
					gen_context(f, item, norm_build)

					f.write('# Build with ASAN\n')
					gen_context(f, item, target)
					gen_version(f)
		print("[OK] successfully generate '"+ out_file +"'")


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
			gen_report(a)

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

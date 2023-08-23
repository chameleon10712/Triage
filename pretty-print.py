import json
import getopt, sys

file_name = ""
out_name = ""

def app(file_name, out_name):
    with open(file_name, "r") as f:
        data = f.read()

    data = data.split('\n')

    with open(out_name, "w") as f:
        for item in data:
            if item != '':
                item = json.loads(item)
                # print(item['poc'])
                f.write(item['poc'])
                f.write('\n')
                for line in item['ASAN']:
                    f.write(line)
                    # print(line)
                    f.write('\n')
                f.write('\n')

        print("[OK] successfully generate " + out_name)

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
			#app()
			pass

        elif o in ("-t", "--triage"):
			file_name = "triage-output.txt"
			out_name = "triage-print.txt"
            app()
        else:
            assert False, "unhandled option"

    if len(sys.argv) == 1:
		file_name = "triage-print.txt"
		out_name = "print.txt"
        app()

import json

with open("output.txt", "r") as f:
    data = f.read()

data = data.split('\n')

with open("print.txt", "w") as f:
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

    print("[OK] successfully generate 'print.txt'")



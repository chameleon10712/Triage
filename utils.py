
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


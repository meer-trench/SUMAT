import os
import sys

checkm_report = sys.argv[1]
bins_path = sys.argv[2]
out_path = sys.argv[3]
out_checkm = sys.argv[4]

if not bins_path.endswith('/'): bins_path += '/'
if not out_path.endswith('/'): out_pat += '/'
if not os.path.isdir(out_path): os.mkdir(out_path)

# Read in checkm report
checkm = []
with open(checkm_report, 'r') as f:
    f.readline()
    for line in f:
        line = line.strip('\n').split('\t')
        checkm.append((line[0], float(line[11]), float(line[12])))

# Cp qualified bins to the output path
count = 0
report = []
for item in checkm:
    label = item[0] + '.fna'
    com = item[1]
    con = item[2]
    score = com - con * 5
    if com >= 50 and con <= 10 and score >= 50:
        report.append((label, com, con))
        cmd = 'cp ' + bins_path + item[0] + '.fna' + ' ' + out_path
        count += 1
        print(cmd)
        os.system(cmd)
print('Found and copy {0} bins to {1}'.format(count, out_path))
with open(out_checkm, 'w') as f:
    for item in report:
        f.write('{0}\n'.format(','.join([str(i) for i in item])))
print('CheckM report wrote to {0}'.format(out_checkm))

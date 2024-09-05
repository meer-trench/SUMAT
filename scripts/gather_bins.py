import os
import sys

bf_path = sys.argv[1]
csv_out = sys.argv[2]
out_path = sys.argv[3]
sample =sys.argv[4]

csv = []

if os.path.isdir(bf_path + 'metawrap_50_10_bins/'):
    bin_passed = []
    with open(bf_path + 'metawrap_50_10_bins.stats', 'r') as f:
        f.readline()
        for line in f:
            line = line.strip('\n').split('\t')
            com = float(line[1])
            con = float(line[2])
            score = com - 5 * con
            print(line[0], com, con, score)
            if com >= 50 and con <= 10 and score >= 50:
                bin_passed.append(sample + '_' + line[0] + '.fa')
                csv.append([sample + '_' + line[0] + '.fa', str(com), str(con)])
    print('Found {0} bins passed Com >= 50, Con <=10, QS >=50'.format(len(bin_passed)))
    print('Cp all bins to {0}'.format(out_path))
    for item in bin_passed:
        cmd = ['cp']
        cmd += [bf_path + 'metawrap_50_10_bins/' + item]
        cmd += [out_path]
        cmd = ' '.join(cmd)
        print(cmd)
        os.system(cmd)
    with open(csv_out, 'w') as f:
        for line in csv:
            line = ','.join(line)
            f.write('{0}\n'.format(line))
    print('CheckM results wrote to {0}'.format(csv_out))

else:
    print('No bin passed score checking for {0}'.format(sample))
    cmd = 'touch ' + csv_out
    print(cmd)
    os.system(cmd)


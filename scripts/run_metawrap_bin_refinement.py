#!/usr/bin/env python

import os
import sys

metabat2 = sys.argv[1]
maxbin2 = sys.argv[2]
concoct = sys.argv[3]
out_path = sys.argv[4]
threads = sys.argv[5]

mb2 = os.path.isdir(metabat2)
ma2 = os.path.isdir(maxbin2)
cct = os.path.isdir(concoct)

if mb2 and ma2 and cct:
    print('-A {0} -B {1} -C {2}'.format(metabat2, maxbin2, concoct))
    cmd = ['metawrap bin_refinement']
    cmd += ['-o ' + out_path]
    cmd += ['-t ' + threads]
    cmd += ['-m 64']
    cmd += ['-A {0} -B {1} -C {2}'.format(metabat2, maxbin2, concoct)]
    cmd += ['-c 50 -x 10']
    cmd = ' '.join(cmd)
    print(cmd)
    os.system(cmd)
elif mb2 and ma2 and (not cct):
    print('-A {0} -B {1}'.format(metabat2, maxbin2))
    cmd = ['metawrap bin_refinement']
    cmd += ['-o ' + out_path]
    cmd += ['-t ' + threads]
    cmd += ['-m 64']
    cmd += ['-A {0} -B {1}'.format(metabat2, maxbin2)]
    cmd += ['-c 50 -x 10']
    cmd = ' '.join(cmd)
    print(cmd)
    os.system(cmd)
elif mb2 and (not ma2) and cct:
    print('-A {0} -B {1}'.format(metabat2, concoct))
    cmd = ['metawrap bin_refinement']
    cmd += ['-o ' + out_path]
    cmd += ['-t ' + threads]
    cmd += ['-m 64']
    cmd += ['-A {0} -B {1}'.format(metabat2, concoct)]
    cmd += ['-c 50 -x 10']
    cmd = ' '.join(cmd)
    print(cmd)
    os.system(cmd)
elif (not mb2) and ma2 and cct:
    print('-A {0} -B {1}'.format(maxbin2, concoct))
    cmd = ['metawrap bin_refinement']
    cmd += ['-o ' + out_path]
    cmd += ['-t ' + threads]
    cmd += ['-m 64']
    cmd += ['-A {0} -B {1}'.format(maxbin2, concoct)]
    cmd += ['-c 50 -x 10']
    cmd = ' '.join(cmd)
    print(cmd)
    os.system(cmd)
elif mb2 and (not ma2) and (not cct):
    print('-A {0}'.format(metabat2))
    cmd = ['mkdir -p']
    cmd += [out_path + 'metawrap_50_10_bins/']
    cmd = ' '.join(cmd)
    print(cmd)
    os.system(cmd)

    cmd = ['cp']
    cmd += [metabat2 + '/bin.*.fa']
    cmd += [out_path + 'metawrap_50_10_bins/']
    cmd = ' '.join(cmd)
    print(cmd)
    os.system(cmd)
elif (not mb2) and ma2 and (not cct):
    print('-A {0}'.format(maxbin2))
    cmd = ['mkdir -p']
    cmd += [out_path + 'metawrap_50_10_bins/']
    cmd = ' '.join(cmd)
    print(cmd)
    os.system(cmd)

    cmd = ['cp']
    cmd += [maxbin2 + '/bin.*.fa']
    cmd += [out_path + 'metawrap_50_10_bins/']
    cmd = ' '.join(cmd)
    print(cmd)
    os.system(cmd)
elif (not mb2) and (not ma2) and cct:
    print('-A {0}'.format(concoct))
    cmd = ['mkdir -p']
    cmd += [out_path + 'metawrap_50_10_bins/']
    cmd = ' '.join(cmd)
    print(cmd)
    os.system(cmd)

    cmd = ['cp']
    cmd += [concoct + '/bin.*.fa']
    cmd += [out_path + 'metawrap_50_10_bins/']
    cmd = ' '.join(cmd)
    print(cmd)
    os.system(cmd)
else:
    cmd = ['mkdir -p']
    cmd += [out_path + 'this_is_not_the_bin_you_are_looking_for/']
    cmd = ' '.join(cmd)
    print(cmd)
    os.system(cmd)

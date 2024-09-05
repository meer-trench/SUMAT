#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

run_pushcore_rename_concat.py -i {input[0]} -o {output.ctg} -w {params.contig_path}

He who loves to comment his code is unlikely to have bad luck.
@author: Song, Zewei
@contact: songzewei@genomics.cn
"""

import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', help='Path to the pushcore path file.')
parser.add_argument('-o', '--output',help='Path to the renamed and concatenated contig file.')
parser.add_argument('-w', '--contigs',  help='Folders contains contigs.')
args=parser.parse_args()

input_path = args.input
output_path = args.output
contigs_path = args.contigs

# Parse the path file
pushcore = {}
with open(input_path, 'r') as f:
    for line in f:
        line = line.strip('\n').split('\t')
        pushcore[line[0]] = pushcore.get(line[0], []) + [line[1]]
print('Found {0} samples for pushcore {1}'.format(len(pushcore), input_path))

# Check if all contigs exist
contigs_list = {}
for f in os.listdir(contigs_path):
    if f.endswith("fa"):
        sn = f.split('.')[0]
        contigs_list[sn] = contigs_path + f

for key in pushcore.keys():
    assert key in contigs_list, "Sample {0} not found in contigs path: {1}".format(key, contigs_path)

cmd = 'touch ' + output_path
print(cmd)
os.system(cmd)

for key in pushcore.keys():
    cmd = ['seqtk rename']
    cmd += [contigs_list[key]]
    cmd += [key + '@ctg_']
    cmd += ['|']
    cmd += ['seqtk seq -L 1000 - | seqtk seq -C - >>']
    cmd += [output_path]
    cmd = ' '.join(cmd)
    print(cmd)
    os.system(cmd)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 30 11:02:18 2022

run_fastp.py -i sample.path.tsv -t {threads} -o sample.merged.fa.gz -f sample.unmerged.1.fa.gz -r sample.unmegred.2.fa.gz

@author: songz
"""

import argparse
import os
import sys
import hashlib
# from zetaSeq import io as seqIO

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', help='Path to the sample path tav file.')
# parser.add_argument('-w', '--raw', default='/')
parser.add_argument('-w', '--raw', default='/hwfssz1/ST_HEALTH/P18Z10200N0059/fangchao/MEER/DATA/MEER_RAW_CENTER/', help='Path to the raw data')
parser.add_argument('-t', '--threads', type=int, help='Number of threads.')
parser.add_argument('-o', '--output', help='Path to merged file.')
parser.add_argument('-f', '--forward', help='Path to unmerged r1 file.')
parser.add_argument('-r', '--reverse', help='Path to unmerged r2 file.')
#parser.add_argument('-ad1', help='Forward adaptor sequence.')
#parser.add_argument('-ad2', help='Reverse adaptor sequence.')
parser.add_argument('-log', default='log.tsv', help='Path to log file.')
parser.add_argument('-tmp', default='TMP/', help='Path to tmp file.')
parser.add_argument('-d', '--dry_run', action='store_true', help='Indicator of dry-run.')
args=parser.parse_args()
input_file = args.input
raw_path = args.raw
if not raw_path.endswith('/'): raw_path += '/'
threads = int(args.threads/2)
merged_file = args.output
unmerged_file = (args.forward, args.reverse)
#ad1 = args.ad1
#ad2 = args.ad2
log_file = args.log
dry_run = args.dry_run
tmp_path = args.tmp
# Check if input file ends with .gz
if merged_file.endswith('.gz'):
    pass
else:
    print('Input file has to be .gz')
    sys.exit()
if unmerged_file[0].endswith('.gz'):
    pass
else:
    print('Input file has to be .gz')
    sys.exit()
if unmerged_file[1].endswith('.gz'):
    pass
else:
    print('Input file has to be .gz')
    sys.exit()

# Get FASTQ path
path= {}
with open(input_file, 'r') as f: # Each line is a path to a sequencing lane
    for line in f:
        line = line.strip('\n')
        content = []
        for file in os.listdir(raw_path + line):
            if file.endswith('.fq.gz'):
                content.append(file)
        content.sort()
        if len(content) != 2:
            print('Wrong file number.')
            sys.exit()
        path[line] = tuple(content)

# Run fastp
tmp = []
for key, value in path.items():
    print('Run fastp on path {0}'.format(key))
    hash_object = hashlib.md5((input_file+key).encode())
    tmp_seq = tmp_path + 'tmp_' + hash_object.hexdigest()
    tmp.append(tmp_seq)
    cmd = ['fastp']
    cmd += ['-i ' + raw_path + key + '/' + value[0]]
    cmd += ['-I ' + raw_path + key + '/' + value[1]]
    cmd += ['-m --merged_out ' + tmp_seq + '.merged.fq.gz']
    cmd += ['--out1 ' + tmp_seq + '.unmerged.1.fq.gz']
    cmd += ['--out2 ' + tmp_seq + '.unmerged.2.fq.gz']
 #   cmd += ['--adapter_sequence ' + ad1]
 #   cmd += ['--adapter_sequence_r2 ' + ad2]
    cmd += ['--length_required 100']
    cmd += ['--cut_front --cut_right -W 4 -M 20']
    cmd += ['-w ' + str(threads)]
    cmd += ['-j ' + log_file]
    print(' '.join(cmd))
    if not dry_run:
        os.system(' '.join(cmd))
    print('Finished fastp on path {0}'.format(key))

# Concat all finished file, and remove the temp files
output_merged = []
output_unmerged_r1 = []
output_unmerged_r2 = []
if dry_run:
    print('Write merged to {0}'.format(merged_file))
    print('Write unmerged to {0} {1}'.format(unmerged_file[0], unmerged_file[1]))
else:
    cmd1 = ['seqtk seq -A', tmp[0] + '.merged.fq.gz', '>', merged_file[:-3]]
    cmd2 = ['seqtk seq -A', tmp[0] + '.unmerged.1.fq.gz', '>', unmerged_file[0][:-3]]
    cmd3 = ['seqtk seq -A', tmp[0] + '.unmerged.2.fq.gz', '>', unmerged_file[1][:-3]]
    print(' '.join(cmd1))
    if not dry_run: os.system(' '.join(cmd1))
    print(' '.join(cmd2))
    if not dry_run: os.system(' '.join(cmd2))
    print(' '.join(cmd3))
    if not dry_run: os.system(' '.join(cmd3))
    if len(tmp) > 1: # If more than one path presents
        for item in tmp[1:]:
            cmd1 = ['seqtk seq -A', item + '.merged.fq.gz', '>>', merged_file[:-3]]
            cmd2 = ['seqtk seq -A', item + '.unmerged.1.fq.gz', '>>', unmerged_file[0][:-3]]
            cmd3 = ['seqtk seq -A', item + '.unmerged.2.fq.gz', '>>', unmerged_file[1][:-3]]
            print(' '.join(cmd1))
            if not dry_run: os.system(' '.join(cmd1))
            print(' '.join(cmd2))
            if not dry_run: os.system(' '.join(cmd2))
            print(' '.join(cmd3))
            if not dry_run: os.system(' '.join(cmd3))

# Pigz all FASTA files
cmd = ['pigz']
cmd += ['-p ' + str(threads)]
cmd += [merged_file[:-3]]
print(' ' .join(cmd))
if not dry_run: os.system(' '.join(cmd))

cmd = ['pigz']
cmd += ['-p ' + str(threads)]
cmd += [unmerged_file[0][:-3]]
print(' '.join(cmd))
if not dry_run: os.system(' '.join(cmd))

cmd = ['pigz']
cmd += ['-p ' + str(threads)]
cmd += [unmerged_file[1][:-3]]
print(' '.join(cmd))
if not dry_run: os.system(' '.join(cmd))


# Remove TMP files
if dry_run:
    pass
else:
    for item in tmp:
        os.remove(item + '.merged.fq.gz')
        os.remove(item + '.unmerged.1.fq.gz')
        os.remove(item + '.unmerged.2.fq.gz')
print('TMP files removed')
print('QCed files in {0} {1} {2}'.format(merged_file, unmerged_file[0], unmerged_file[1]))

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 30 11:02:18 2022

run_pushcore_fastp.py -i pushcore.path -t {threads} -w [RAW/] -o /path/to/the/pushcore/ -ad1 [AD1] -ad2 [AD2] -log [LOG] [-d]

@author: songz
"""

import argparse
import os
import sys
import hashlib
# from zetaSeq import io as seqIO

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', help='Path to the pushcore path tav file.')
parser.add_argument('-w', '--raw', default='/', help='Path to the raw data')
parser.add_argument('-t', '--threads', type=int, help='Number of threads.')
parser.add_argument('-o', '--output', help='Path to the output folder for all samples.')
parser.add_argument('-s', '--sequencer', choices=['mgi', 'other'], default='mgi', help='Sequencers')
parser.add_argument('-log', default='log.tsv', help='Path to log file.')
parser.add_argument('-d', '--dry_run', action='store_true', help='Indicator of dry-run.')
args=parser.parse_args()

input_file = args.input
raw_path = args.raw
if not raw_path.endswith('/'): raw_path += '/'
threads = args.threads
mgi = False
if args.sequencer == 'mgi':
    mgi = True
    ad1 = 'AAGTCGGAGGCCAAGCGGTCTTAGGAAGACAA'
    ad2 = 'AAGTCGGATCGTAGCCATGTCGTTCTGTGAGCCAAGGAGTTG'
output_path = args.output
if not output_path.endswith('/'): output_path += '/'
if not os.path.isdir(output_path): os.mkdir(output_path)
log_file = args.log
dry_run = args.dry_run

# Get per sample path
pushcore = {}
with open(input_file, 'r') as f:
    for line in f:
        line = line.strip('\n').split('\t')
        pushcore[line[0]] = pushcore.get(line[0], []) + [line[1]]
print('Pushcore ({0}) contains {1} samples'.format(input_file, len(pushcore)))

# Get per path FASTQ files
path_fastq = {}
for key, value in pushcore.items():
    for path in value:
        path_fastq[path] = []
        for file in os.listdir(raw_path + path):
            if file.endswith('.fq.gz') or file.endswith('.fastq'):
                path_fastq[path].append(file)
        path_fastq[path].sort()
        if len(path_fastq[path]) != 2:
            print('Wrong file number!')
            sys.exit()    

# fastp this pushcore per sample per path
for sample in pushcore.keys():
    tmp = []
    unmerged_file = []
    unmerged_file.append(output_path + sample + '.unmerged.1.fq.gz')
    unmerged_file.append(output_path + sample + '.unmerged.2.fq.gz')
    for path in pushcore[sample]:
        print('Run fastp on Sample: {0} and Path: {1}'.format(sample, path))
        hash_object = hashlib.md5((input_file+sample+path+'pushcore').encode())
        tmp_seq = 'TMP/tmp_' + hash_object.hexdigest()
        tmp.append(tmp_seq)
        cmd = ['fastp']
        cmd += ['-i ' + raw_path + path + '/' + path_fastq[path][0]]
        cmd += ['-I ' + raw_path + path + '/' + path_fastq[path][1]]
        cmd += ['--out1 ' + tmp_seq + '.unmerged.1.fq.gz']
        cmd += ['--out2 ' + tmp_seq + '.unmerged.2.fq.gz']
        if mgi: cmd += ['--adapter_sequence ' + ad1]
        if mgi: cmd += ['--adapter_sequence_r2 ' + ad2]
        cmd += ['--length_required 100']
        cmd += ['--cut_front --cut_right -W 4 -M 20']
        cmd += ['-w ' + str(threads)]
        cmd += ['-j ' + log_file]
        print(' '.join(cmd))
        if not dry_run:
            os.system(' '.join(cmd))
        print('Finished fastp on path {0}'.format(key))

    # Concat all finished file, and remove the temp files
    print('Write unmerged to {0} {1}'.format(unmerged_file[0], unmerged_file[1]))
    cmd2 = ['seqtk seq ', tmp[0] + '.unmerged.1.fq.gz', ' > ', unmerged_file[0][:-3]]
    cmd3 = ['seqtk seq ', tmp[0] + '.unmerged.2.fq.gz', ' > ', unmerged_file[1][:-3]]
    print(' '.join(cmd2))
    if not dry_run: os.system(' '.join(cmd2))
    print(' '.join(cmd3))
    if not dry_run: os.system(' '.join(cmd3))
    if len(tmp) > 1: # If more than one path presents
        for item in tmp[1:]:
            cmd2 = ['seqtk seq ', item + '.unmerged.1.fq.gz', ' >> ', unmerged_file[0][:-3]]
            cmd3 = ['seqtk seq ', item + '.unmerged.2.fq.gz', ' >> ', unmerged_file[1][:-3]]
            print(' '.join(cmd2))
            if not dry_run: os.system(' '.join(cmd2))
            print(' '.join(cmd3))
            if not dry_run: os.system(' '.join(cmd3))

    # Remove TMP files
    if dry_run:
        pass
    else:
        for item in tmp:
            os.remove(item + '.unmerged.1.fq.gz')
            os.remove(item + '.unmerged.2.fq.gz')
    print('TMP files removed')
    print('QCed files for {0} in {1} {2}'.format(sample, unmerged_file[0], unmerged_file[1]))

    # Pigz all FASTA files
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

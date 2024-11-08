#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Fri May 13 15:47:00 2022

Create input files for Snakemake from the raw data.

allocate_runs_to_samples.py -i metadata.tsv -r /path/to/the/rawdata/ \
    -d /path/to/the/target_dir/ -l log.tsv

He who loves to comment his code is unlikely to have bad luck.
@author: Song, Zewei
@contact: songzewei@genomics.cn
"""

import argparse
import os
import sys

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', default='metadata.tsv', help='Path to the overral metadata.')
# parser.add_argument('-s', '--samples', help='Path to a list of sample names.'
parser.add_argument('-d', '--destiny', help='Path to the snakemake working directory.')
parser.add_argument('-r', '--raw', help='Path to the raw data.')
parser.add_argument('-l', '--log', default='log.tsv', help='Path to the log file.')
args = parser.parse_args()
input_file = args.input
destiny_path = args.destiny
if not destiny_path.endswith('/'): destiny_path += '/'
raw_path = args.raw
if not raw_path.endswith('/'): raw_path += '/'
log_file = args.log
with open(log_file, 'w') as f:
    f.write('Sample_name\tNumber_of_lanes\n')

# Parse the metadata
samples = {}
pushcores = {}
with open(input_file, 'r') as f:
    for line in f:
        line = line.strip('\n').split('\t')
        sn = line[0].replace('/', '-')
        samples[sn] = samples.get(sn, []) + [line[2]]
        ps = line[3]
        pushcores[ps] =pushcores.get(ps,[])+[line[0]]

# Find samples available on current cluster
samples_avail = {}
for key, value in samples.items():
    path_checker = [False] * len(value) # check if all paths are available for current sample
    for index, path in enumerate(value):
        # check if we have two fq.gz files under current path
        #file_checker = [False, False]
        fq_files = []
        #try:
        for file in os.listdir(raw_path + path):
            if file.endswith('.fq.gz') or file.endswith('fastq.gz'):
                fq_files.append(file)
        fq_files.sort()
        #if len(fq_files) == 2 and fq_files[0].endswith('_1.fq.gz') and fq_files[1].endswith('_2.fq.gz'):
        #    path_checker[index] = True
        #except FileNotFoundError:
            #path_checker[index] = False
    #if sum(path_checker) == len(path_checker): # If pass the check
    samples_avail[key] = tuple(value)
    with open(log_file, 'a') as f:
        f.write('{0}\t{1}\n'.format(key, len(value)))
    #else:
    
    #with open(log_file, 'a') as f:
    #        f.write('{0}\t{1}\n'.format(key, 0))

print('Found {0}/{1} samples under {2}'.format(len(samples_avail), len(samples), raw_path))

# Write samples to destiny
if not os.path.isdir(destiny_path + 'data/samples/'):
    if not os.path.isdir(destiny_path): os.mkdir(destiny_path)
    if not os.path.isdir(destiny_path + 'data/'): os.mkdir(destiny_path + 'data/')
    if not os.path.isdir(destiny_path + 'data/samples/'):
        os.mkdir(destiny_path + 'data/samples/')
else:
    if len(os.listdir(destiny_path + 'data/samples/')) > 0: # the destiny folder is NOT empty
        print('{0} is not empty, please check.'.format(destiny_path + 'data/samples/'))
        sys.exit()
    else:
        print('{0} is ready.'.format(destiny_path + 'data/samples'))
for key, value in samples_avail.items():
    target_file = destiny_path + 'data/samples/' + key + '.path'
    with open(target_file, 'w') as f:
        for item in value:
            f.write('{0}\n'.format(item))

if not os.path.isdir(destiny_path + 'data/pushcores/'):
    os.mkdir(destiny_path + 'data/pushcores/')

for key, value in pushcores.items():
    target_file = destiny_path + 'data/pushcores/' + key + '.path'
    with open(target_file, 'w') as f:
        for item in value:
            for k,v in samples_avail.items():
                if k == item:
                    for i in v:
                        str= item +"\t"+i+"\n"
                        f.write(str)

print('Input files for Snakemake is ready at {0}'.format(destiny_path + 'data/samples/'))
print('Check log file: {0}'.format(log_file))

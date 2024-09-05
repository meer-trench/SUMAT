#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 30 11:02:18 2022

run_pushcore_bwa.py -i pushcore.path -t {threads} -r /path/ref/contigs/{pushcore}.contigs.fa -q /path/to/fastp/pushcore/ -o /path/to/the/pushcore/  -log [LOG] [-d]

run_pushcore_bwa.py -i {input.pc} -r {params.index_path} -o {params.out_path} -t {threads}

@author: songz
"""

import argparse
import os
import sys
import hashlib
# from zetaSeq import io as seqIO

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', help='Path to the sample path tsv file.')
parser.add_argument('-f', '--fastq', help='Path to the QCed fasta files.')
parser.add_argument('-r', '--index', help='Path to the bwa index.')
parser.add_argument('-t', '--threads', type=int, help='Number of threads.')
parser.add_argument('-o', '--output', help='Path to bwa output folder.')
parser.add_argument('-d', '--dry_run', action='store_true', help='Indicator of dry-run.')
args=parser.parse_args()
input_file = args.input
pn = os.path.basename(input_file).split('.')[0]
fastq_path = args.fastq
if not fastq_path.endswith('/'): fastq_path += '/'
index_path = args.index
threads = args.threads
output_path = args.output
if not output_path.endswith('/'): output_path += '/'
if not os.path.isdir(output_path): os.mkdir(output_path)
dry_run = args.dry_run
if dry_run:
    print('THIS IS A DRY RUN')

# Get sample names belong to this pushcore
pushcore = {}
with open(input_file, 'r') as f:
    for line in f:
        line = line.strip('\n').split('\t')
        pushcore[line[0]] = []
print('Pushcore ({0}) contains {1} samples'.format(input_file, len(pushcore)))


# Add the QCed fasta to each sample
for sample in pushcore.keys():
    fastq = (fastq_path + '/' + sample + '.unmerged.1.fq.gz', fastq_path + '/' + sample + '.unmerged.2.fq.gz')
    print(fastq)
    if os.path.isfile(fastq[0]) and os.path.isfile(fastq[1]):
        pushcore[sample] = fastq
    else:
        print('For pushcore {0}, sample {1} not found matched fastq data'.format(pn, sample))
        sys.exit(1)


def bwa(index, threads, fq, output, dr):
    cmd = ['bwa mem']
    cmd += ['-t ' + str(threads)]
    cmd += [index]
    cmd += [fq[0] + ' ' + fq[1]]
    cmd += ['| ' + 'samtools sort ' + '-@ ' + str(threads) +  ' -o ' + output + ' -']
    cmd = ' '.join(cmd)
    print(cmd)
    if not dr: os.system(cmd)
    return 0


# BWA alignment per sample
for key, value in pushcore.items():
    sorted_bam = output_path + key + '.sorted.bam'
    print('BWA mem sample {0} to {1}'.format(key, sorted_bam))
    bwa(index_path, threads, value, sorted_bam, dry_run)


# Check all sorted bam is ready
if not dry_run:
    for key, value in pushcore.items():
        sorted_bam = output_path + key + '.sorted.bam'
        if os.path.isfile(sorted_bam):
            print('All sorted bam files in place, checked.')
        else:
            print('Not found sorted bam for sample {0}'.format(key))
            sys.exit(1)

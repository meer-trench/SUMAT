configfile: 'config.yaml'

import os
import sys
SAMPLES = {}
PUSHCORES ={}
path = config['location']
if not path.endswith('/'): path += '/'
sample_path = path + 'data/samples/'
group_path = path + 'data/pushcores/'

folder_checks = [path + 'TMP/', path + 'data/contigs',
                 path + 'data/binning/',
                 path + 'data/bin_refinement/',
                 path + 'data/bin_passed_all/',
                 path + 'data/contigs_for_binning/',
                 path + 'data/gather_all_checkm_csv/']

if config['resources'] == 'Sufficient':
    folder_checks.extend([path + 'data/pushcore_fastp/',
                 path + 'data/pushcore_bwa_index/',
                 path + 'data/pushcore_bwa_mem/',
                 path + 'data/pushcore_vamb_bins/',
                 path + 'data/pushcore_bin_refinement/',
                 path + 'data/pushcore_bin_passed_all/',
                 path + 'data/pushcore_gather_all_checkm/'])

    for file in os.listdir(group_path):
        if file.endswith('.path'):
            pushcore_name = file.split('.')[0]
            PUSHCORES[pushcore_name] = PUSHCORES.get(pushcore_name, []) + [group_path + file]

        if len(PUSHCORES) == 0:
            print('ERROR: no file under {0}.'.format(filepath))
            sys.exit('Pipeline terminated orz.')
        else:
            for key, value in PUSHCORES.items():
                if len(value) != 1:
                    print('{0} does not have the right files.'.format(key))
                    sys.exit('Pipeline terminated, please check.')
                else:
                    PUSHCORES[key] = tuple(sorted(value))

for item in folder_checks:
    print(item)
    if not os.path.isdir(item): os.mkdir(item)

for file in os.listdir(sample_path):
    if file.endswith('.path'):
        sample_name = file.split('.')[0]
        SAMPLES[sample_name] = SAMPLES.get(sample_name, []) + [sample_path + file]

if len(SAMPLES) == 0:
    print('ERROR: no file under {0}.'.format(filepath))
    sys.exit('Pipeline terminated orz.')
else:
    for key, value in SAMPLES.items():
        if len(value) != 1:
            print('{0} does not have the right files.'.format(key))
            sys.exit('Pipeline terminated, please check.')
        else:
            SAMPLES[key] = tuple(sorted(value))

rule all:
    input:
        profile = path + 'data/markers/profile_mk/all.mk',
        mags = path + 'data/markers/mags_mk/all.mk'

rule target_profile:
    input:
        (path + 'data/markers/profiling_fpkm_all/all.mk',path + 'data/markers/metaphlan4_mk/all.mk',path + 'data/markers/kraken2_mk/all.mk') if config['resources'] == 'Sufficient' else (
            path + 'data/markers/metaphlan4_mk/all.mk' if config['novelty'] == 'Low' else path + 'data/markers/kraken2_mk/all.mk'
        )
    output:
        mk = path + 'data/markers/profile_mk/all.mk'
    shell:
        """
        touch {output.mk}
        """

rule target_mags:
    input:
        mk = path + 'data/markers/drep_all_99.mk'
    output:
        mk = path + 'data/markers/mags_mk/all.mk'
    shell:
        """
        touch {output.mk}
        """

rule fastp_not_merged:
    input:
        lambda wildcards: SAMPLES[wildcards.sample]
    output:
        a1 = path + 'data/fastp_not_merged/{sample}.unmerged_1.fa.gz'
    threads: config['fastp']['t']
    params:
        a2 = path + 'data/fastp_not_merged/{sample}.unmerged_2.fa.gz',
        sq = config['data_type'],
        sn = '{sample}',
        raw = config['location'],
        path = path + 'data/contigs/{sample}/',
	tmp_path = path + '/TMP/',
        #r1 = config['adapter1'],
        #r2 = config['adapter2']
    log: path + 'logs/fastp_not_merged/{sample}.json'
    shell:
        """
        if [ "{params.sq}" == "pe" ]; then
            scripts/run_fastp_not_merge.py -i {input[0]} -w {params.raw}/raw_data -f {output.a1} -r {params.a2} -t {threads} -log {log} -tmp {params.tmp_path}
            if [ "$?" -ne 0 ]; then exit 1; fi
	else
            scripts/run_fastp_not_merge.py -i {input[0]} -w {params.raw}/raw_data -f {output.a1}  -t {threads} -log {log} -tmp {params.tmp_path}
	    if [ "$?" -ne 0 ]; then exit 1; fi
        fi
        """

rule fastp:
    input:
        lambda wildcards: SAMPLES[wildcards.sample]
    output:
        ma = path + 'data/fastp_merged/{sample}.merged.fa.gz',
        a1 = path + 'data/fastp_merged/{sample}.unmerged.1.fa.gz',
        a2 = path + 'data/fastp_merged/{sample}.unmerged.2.fa.gz'
    threads: config['fastp']['t']
    params:
        sq = config['data_type'],
        sn = '{sample}',
	tmp_path = path + '/TMP/',
        raw = config['location'],
        path = path + 'data/contigs/{sample}/',
        #r1 = config['adapter1'],
        #r2 = config['adapter2']
    log: path + 'logs/fastp_merged/{sample}.json'
    shell:
        """
        python3 scripts/run_fastp.py -i {input[0]} -w {params.raw}/raw_data -o {output.ma} -f {output.a1} -r {output.a2} -t {threads} -log {log} -tmp {params.tmp_path}
        """

rule pushcore_fastp:
    input:
        pc = path + 'data/pushcores/{pushcore}.path'
    output:
        mk = path + 'data/markers/pushcore_fastp/{pushcore}.mk'
    params:
        #r1 = config['adapter1'],
        #r2 = config['adapter2'],
        out_path = path + 'data/pushcore_fastp/{pushcore}/',
	tmp_path = path + '/TMP/',
        raw = config['location']
    threads: config['fastp']['t']
    shell:
        """
        python scripts/run_pushcore_fastp.py -i {input.pc} -o {params.out_path} -t {threads} -w {params.raw}/raw_data -tmp {params.tmp_path}
        touch {output.mk}
        """

rule megahit:
    input:
        ma = path + 'data/fastp_merged/{sample}.merged.fa.gz',
        a1 = path + 'data/fastp_merged/{sample}.unmerged.1.fa.gz',
        a2 = path + 'data/fastp_merged/{sample}.unmerged.2.fa.gz'
    output:
        mk = path + 'data/markers/megahit_pe_mk/{sample}.mk',
    threads: config['megahit']['t']
    params:
        sq = config['data_type'],
        sn = '{sample}',
        path = path + 'data/contigs/{sample}/'
    shell:
        """
        #if [ -d "{params.path}" ];then rm -r {params.path};else echo Folder not exist, MEGAHIT good to go.;fi
        if [ -d "{params.path}" ]; then megahit --continue -o {params.path}; else megahit -1 {input.a1} -2 {input.a2} -r {input.ma} -t {threads} --presets meta-sensitive -o {params.path}; fi
        #megahit -1 {input.a1} -2 {input.a2} -r {input.ma} -t {threads} --presets meta-sensitive -o {params.path}
        touch {output.mk}
        """

rule megahit_se:
    input:
        a1 = path + 'data/fastp_not_merged/{sample}.unmerged_1.fa.gz'
    output:
        mk = path + 'data/markers/megahit_se_mk/{sample}.mk',
    threads: config['megahit']['t']
    params:
        sq = config['data_type'],
        sn = '{sample}',
        path = path + 'data/contigs/{sample}/'
    shell:
        """
        #if [ -d "{params.path}" ];then rm -r {params.path};else echo Folder not exist, MEGAHIT good to go.;fi
        if [ -d "{params.path}" ]; then megahit --continue -o {params.path}; else megahit -1 {input.a1} -t {threads} --presets meta-sensitive -o {params.path}; fi
        """

rule megahit_result:
    input:
        mk = path + 'data/markers/megahit_se_mk/{sample}.mk' if config['data_type'] == 'se' else (
            path + 'data/markers/megahit_pe_mk/{sample}.mk'
        )
    output:
        fa = path + 'data/contigs_for_binning/{sample}.final.contigs.fa',
        mk = path + 'data/markers/megahit_mk/{sample}.mk'
    params:
        fa = path + 'data/contigs/{sample}/final.contigs.fa',
        sn = '{sample}'
    shell:
        """
        seqtk rename {params.fa} {params.sn}@ctg_ | seqtk seq -L 1000 - | seqtk seq -C - > {output.fa}
        touch {output.mk}
        """


rule kraken2:
    input:
        a1 = path + 'data/fastp_not_merged/{sample}.unmerged_1.fa.gz',
    output:
        mk = path + 'data/markers/kraken2_mk/{sample}.mk',
        report = path + 'data/kraken2/{sample}/{sample}.report',
        breport = path + 'data/kraken2/{sample}/{sample}.breport'
    threads: config['kraken2']['t']
    params:
        sn = '{sample}',
        path = path + 'data/kraken2/{sample}/',
        db = config['kraken2_db']
    shell:
        """
        kraken2  --use-names --db {params.db} --threads {threads} --output {params.path} --report {output.report}  {input.a1}
        bracken -d {params.db} -i {output.report}  -o {output.breport} -l S
        touch {output.mk}
        """

rule combine_kraken2:
    input:
        report = expand(path + 'data/kraken2/{sample}/{sample}.breport', sample=SAMPLES)
    output:
        mk = path + 'data/markers/kraken2_mk/all.mk',
        report = path + 'data/profile/all.kraken2.report'
    params:
        breport = path + 'data/kraken2/*/*.breport'
    threads: 1
    shell:
        """
        combine_bracken_outputs.py --files {params.breport} -o {output.report}
        touch {output.mk}
        """

rule metaphlan4:
    input:
        a1 = path + 'data/fastp_not_merged/{sample}.unmerged_1.fa.gz',
    output:
        mk = path + 'data/markers/metaphlan4_mk/{sample}.mk',
        profile = path + 'data/metaphlan4/{sample}/{sample}.metaphlan4.tsv'
    threads: config['metaphlan4']['t']
    params:
        sn = '{sample}',
        path = path + 'data/metaphlan4/{sample}/',
        #db = config['mp_db']
    shell:
        """
        metaphlan --input_type fasta -t rel_ab -o {output.profile} --nproc {threads} --unclassified_estimation --bowtie2out {params.path}/{wildcards.sample}.bowtie2.txt  {input.a1}
        touch {output.mk}
        """

rule combine_metaphlan4:
    input:
        report = expand(path + 'data/metaphlan4/{sample}/{sample}.metaphlan4.tsv', sample=SAMPLES)
    output:
        mk = path + 'data/markers/metaphlan4_mk/all.mk',
        report = path + 'data/profile/all.metaphlan4.tsv'
    threads: 1
    shell:
        """
        merge_metaphlan_tables.py -o {output.report} {input.report}
        touch {output.mk}
        """

rule binning_create_bam:
    input:
        a1 = path + 'data/fastp_not_merged/{sample}.unmerged_1.fa.gz',
        ctg = path + 'data/contigs_for_binning/{sample}.final.contigs.fa'
    output:
        bam = path + 'data/binning/{sample}/work_files/{sample}.unmerged.bam',
        mk = path + 'data/markers/metawrap_binning_bam/{sample}.mk'
    threads: config['align']['t']
    params:
        path = path + 'data/binning/{sample}/work_files',
        a2 = path + 'data/fastp_not_merged/{sample}.unmerged_2.fa.gz',
        sq = config['data_type']
    shell:
        """
        set +e
        bwa index {input.ctg}
        if [ "{params.sq}" == "pe" ]; then
            bwa mem -v 1 -t {threads} {input.ctg} {input.a1} {params.a2} |samtools sort -@ {threads} -O BAM -o {output.bam}
        else
            bwa mem -v 1 -t {threads} {input.ctg} {input.a1} |samtools sort -@ {threads} -O BAM -o {output.bam}
        fi
	samtools index {output.bam}
        touch {output.mk}
        """

rule binning_metabat2:
    input:
        bam = path + 'data/binning/{sample}/work_files/{sample}.unmerged.bam',
        ctg = path + 'data/contigs_for_binning/{sample}.final.contigs.fa'
    output:
        mk = path + 'data/markers/metawrap_binning_metabat2/{sample}.mk'
    threads: config['binning']['t']
    params:
        path = path + 'data/binning/{sample}/'
    shell:
        """
        set +e
        jgi_summarize_bam_contig_depths --outputDepth {params.path}/work_files/metabat_depth.txt {input.bam}
        metabat2 -i {input.ctg} -a {params.path}/work_files/metabat_depth.txt -o {params.path}/metabat2_bins/bin -m 1500 -t {threads} --unbinned
        touch {output.mk}
        """

rule binning_maxbin2:
    input:
        bam = path + 'data/binning/{sample}/work_files/{sample}.unmerged.bam',
        ctg = path + 'data/contigs_for_binning/{sample}.final.contigs.fa'
    output:
        mk = path + 'data/markers/metawrap_binning_maxbin2/{sample}.mk'
    threads: config['binning']['t']
    params:
        path = path + 'data/binning/{sample}/',
    shell:
        """
        set +e
        mkdir  {params.path}/maxbin2_bins
        #source activate metawrap-env
        jgi_summarize_bam_contig_depths --outputDepth {params.path}/work_files/mb2_master_depth.txt --noIntraDepthVariance {input.bam}
        #calculate total numper of columns
        A=($(head -n 1 {params.path}/work_files/mb2_master_depth.txt))
        N=${{#A[@]}}

            # split the contig depth file into multiple files
        for i in $(seq 4 $N); do
                    samplename=$(head -n 1 {params.path}/work_files/mb2_master_depth.txt | cut -f $i)
                    grep -v totalAvgDepth {params.path}/work_files/mb2_master_depth.txt | cut -f 1,$i > {params.path}/work_files/mb2_${{samplename%.*}}.txt
                    echo {params.path}/work_files/mb2_${{samplename%.*}}.txt >> {params.path}/work_files/mb2_abund_list.txt
        done
        conda run -n metawrap-env run_MaxBin.pl -contig {input.ctg} -markerset 40 -thread {threads} -min_contig_length 1500 -out {params.path}/maxbin2_bins/bin -abund_list {params.path}/work_files/mb2_abund_list.txt
        touch {output.mk}
        """


rule binning_concoct:
    input:
        bam = path + 'data/binning/{sample}/work_files/{sample}.unmerged.bam',
        ctg = path + 'data/contigs_for_binning/{sample}.final.contigs.fa'
    output:
        mk = path + 'data/markers/metawrap_binning_concoct/{sample}.mk'
    threads: config['binning']['t']
    params:
        path = path + 'data/binning/{sample}/'
    shell:
        """
        set +e
	mkdir {params.path}/concoct_bins
        cut_up_fasta.py {input.ctg} -c 10000 --merge_last -b {params.path}/work_files/assembly_10K.bed -o 0 > {params.path}/work_files/assembly_10K.fa
        concoct_coverage_table.py {params.path}/work_files/assembly_10K.bed {input.bam} > {params.path}/work_files/concoct_depth.txt
        concoct -l 1500 -t {threads} --coverage_file {params.path}/work_files/concoct_depth.txt --composition_file {params.path}/work_files/assembly_10K.fa -b {params.path}/work_files/
        merge_cutup_clustering.py {params.path}/work_files/clustering_gt1500.csv > {params.path}/work_files/clustering_gt1500_merged.csv
        split_concoct_bins.py {params.path}work_files/clustering_gt1500_merged.csv {input.ctg} {params.path}/concoct_bins
        touch {output.mk}
        """


rule metawrap_bin_refinement:
    input:
        mk_1 = path + 'data/markers/metawrap_binning_metabat2/{sample}.mk',
        mk_2 = path + 'data/markers/metawrap_binning_maxbin2/{sample}.mk',
        mk_3 = path + 'data/markers/metawrap_binning_concoct/{sample}.mk'
    output:
        mk = path + 'data/markers/metawrap_bin_refinement/{sample}.mk'
    threads: config['binning']['t']
    params:
        sn = '{sample}',
        path = path + 'data/bin_refinement/{sample}/',
        metabat2 = path + 'data/binning/{sample}/metabat2_bins/',
        maxbin2 = path + 'data/binning/{sample}/maxbin2_bins/',
        concoct = path + 'data/binning/{sample}/concoct_bins/',
        #db = config['checkm_db']
    shell:
        """
        set +e
	#checkm data setRoot {params.db}
        python scripts/run_metawrap_bin_refinement.py {params.metabat2} {params.maxbin2} {params.concoct} {params.path} {threads}
        if [ -d "{params.path}metawrap_50_10_bins/" ]
        then
            for file in $(ls {params.path}metawrap_50_10_bins/)
            do
                mv {params.path}metawrap_50_10_bins/$file {params.path}metawrap_50_10_bins/{params.sn}_$file
            done
        else
            echo No bin refined, do nothing
        fi
        touch {output.mk}
        """


rule gather_all_bins:
    input:
        mk = path + 'data/markers/metawrap_bin_refinement/{sample}.mk'
    output:
        csv = path + 'data/gather_all_checkm_csv/{sample}.csv',
        mk = path + 'data/markers/gather_all_bins/{sample}.mk'
    params:
        in_path = path + 'data/bin_refinement/{sample}/',
        out_path = path + 'data/bin_passed_all/'
    threads: 1
    shell:
        """
        python scripts/gather_bins.py {params.in_path} {output.csv} {params.out_path} {wildcards.sample}
        touch {output.mk}
        """


rule gather_all_checkm_csv:
    input:
        csv = expand(path + 'data/gather_all_checkm_csv/{sample}.csv', sample=SAMPLES)
    output:
        csv = path + 'data/checkm_all_passed_bins.csv'
    threads: 1
    shell:
        """
        touch {output.csv}
        echo "genome,completeness,contamination" > {output.csv}
        cat {input.csv} >> {output.csv}
        """

rule gtdbtk_bins:
    input:
        mk = path + 'data/markers/drep_all_99.mk'
    output:
        mk = path + 'data/markers/gtdbtk_bins.mk'
    params:
        in_path = path + 'data/drep_all_99/dereplicated_genomes/',
        out_path = path + 'data/gtdb_bins/'
    threads: config['gtdbtk']['t']
    shell:
        """
        gtdbtk classify_wf --genome_dir {params.in_path} --out_dir {params.out_path} -x fa --cpus {threads} --pplacer_cpus 2
        touch {output.mk}
        """

rule profiling_bowtie2_index:
    input:
        mk = path + 'data/markers/drep_all_99.mk'
    output:
        mk = path + 'data/markers/profiling_bowtie2_index.mk'
    params:
        in_path = path + 'data/drep_all_99/dereplicated_genomes/',
        out_path = path + 'data/bins_bowtie2_index/'
    threads: config['align']['t']
    shell:
        """
        for i in `ls {params.in_path}`;do
            awk -v f=$i 'FNR==1{sub(".bin","",f);sub("fa","",f)};/^>/{sub(">",">"f,$0)}{print}' {in_path}/$i
        done > drep_all/drep_all.fasta
        bowtie2-build --threads {thread} {params.out_path}/drep_all.fasta {params.out_path}/drep_all
        touch {output.mk}
        """
rule profiling_bowtie2:
    input:
        a1 = path + 'data/fastp_not_merged/{sample}.unmerged_1.fa.gz',
        mk = path + 'data/markers/profiling_bowtie2_index.mk'
    output:
        bam = path + 'data/profiling_bowtie2/{sample}.bam',
        mk = path + 'data/markers/profiling_bowtie2/{sample}.mk'
    params:
        sam = path + 'data/profiling_bowtie2/{sample}.sam',
        in_path = path + 'data/bins_bowtie2_index/',
        a2 = path + 'data/fastp_not_merged/{sample}.unmerged_2.fa.gz',
        sq = config['data_type']
    threads: config['align']['t']
    shell:
        """
        if [ "{params.sq}" == "pe" ]; then
            bowtie2 -p {thread} -x {params.in_path}/drep_all -S {params.sam} -1 {input.a1} -2 {params.a2}
        else
            bowtie2 -p {thread} -x {params.in_path}/drep_all -S {params.sam} -1 {input.a1}
        samtools view -@ {thread} -b {params.sam}| samtools sort -@ {thread} -o {output.bam}
        rm {params.sam}
        touch {output.mk}
        """

rule profiling_fpkm:
    input:
        bam = path + 'data/profiling_bowtie2/{sample}.bam',
        jgi = path + 'data/profiling_jgi_depth/{sample}.jgi'
    output:
        mk = path + 'data/markers/profiling_fpkm/{sample}.mk',
        fpkm = path + 'data/profiling_fpkm/{sample}.fpkm'
    params:
        stat = path + 'data/profiling_fpkm/{sample}.stat',
    shell:
        """
        samtools view -h {input.bam}|samtools stats|grep ^SN | cut -f 2- > {params.stat}
        python scripts/fpkm.py 150 {params.stat} {input.jgi} > {output.fpkm}
        touch {output.mk}
        """

rule profiling_fpkm_all:
    input:
        fpkm = expand(path + 'data/profiling_fpkm/{sample}.fpkm', sample=SAMPLES)
    output:
        mk = path + 'data/markers/profiling_fpkm_all/all.mk',
        profile = path + 'data/results/all.fpkm',
    shell:
        """
        python scripts/mags_profiling.py {input.fpkm} {output.profile}
        touch {output.mk}
        """

rule profiling_jgi_depth:
    input:
        bam = path + 'data/profiling_bowtie2/{sample}.bam',
        mk = path + 'data/markers/profiling_bowtie2/{sample}.mk'
    output:
        mk = path + 'data/markers/profiling_jgi_depth/{sample}.mk',
        jgi = path + 'data/profiling_jgi_depth/{sample}.jgi'
    shell:
        """
        jgi_summarize_bam_contig_depths --noIntraDepthVariance --outputDepth {output.jgi} {input.bam}
        touch {output.mk}
        """

rule checkm:
    input:
        mk = path + 'data/markers/pushcore_vamb/{pushcore}.mk' if config['resources'] == 'Sufficient' else path + 'data/markers/metawrap_binning_metabat2/{sample}.mk' if config['resources'] == 'Shortage' else ''
    output:
        rp = path + 'data/pushcore_checkm/report_{pushcore}.tsv' if config['resources'] == 'Sufficient' else path + 'data/checkm/report_{sample}.tsv' if config['resources'] == 'Shortage' else 'report',
        mk = path + 'data/markers/pushcore_checkm/{pushcore}.mk' if config['resources'] == 'Sufficient' else path + 'data/markers/checkm/{sample}.mk' if config['resources'] == 'Shortage' else 'data/markers/checkm/no.mk'
    threads: config['checkm']['t']
    params:
        sn = '{pushcore}' if config['resources'] == 'Sufficient' else '{sample}' if config['resources'] == 'Shortage' else None,
        out_path = path + 'data/pushcore_checkm/{pushcore}/' if config['resources'] == 'Sufficient' else path + 'data/checkm/{sample}/'  if config['resources'] == 'Shortage' else '',
        in_path = path + 'data/pushcore_vamb_bins/{pushcore}/bins/' if config['resources'] == 'Sufficient' else  path + 'data/binning/{sample}/metabat2_bins/'  if config['resources'] == 'Shortage' else ''
    shell:
        """
	#for file in {params.in_path}*.fa; do mv $file {params.in_path}$(basename $file .fa).fna; done
        checkm lineage_wf {params.in_path} {params.out_path} -t {threads} -x fna -f {output.rp} --tab_table
        touch {output.mk}
        """


rule gather_vamb_bins:
    input:
        rp = path + 'data/pushcore_checkm/report_{pushcore}.tsv',
        mk = path + 'data/markers/pushcore_checkm/{pushcore}.mk'
    output:
        csv = path + 'data/pushcore_gather_all_checkm_csv/{pushcore}.csv',
        mk = path + 'data/markers/pushcore_gather_all_bins/{pushcore}.mk'
    params:
        in_path  = path + 'data/pushcore_vamb_bins/{pushcore}/bins/',
        out_path = path + 'data/pushcore_bin_passed_all/'
    threads: 1
    shell:
        """
        python scripts/gather_checkm_bins.py {input.rp} {params.in_path} {params.out_path} {output.csv}
        touch {output.mk}
        """

rule gather_metabat2_bins:
    input:
        rp = path + 'data/checkm/report_{sample}.tsv',
        mk = path + 'data/markers/checkm/{sample}.mk'
    output:
        csv = path + 'data/gather_all_checkm_csv_metabat2/{sample}.csv',
        mk = path + 'data/markers/gather_all_bins_metabat2/{sample}.mk'
    params:
        in_path  =path + 'data/binning/{sample}/metabat2_bins/',
        out_path = path + 'data/bin_passed_all/'
    threads: 1
    shell:
        """
        python scripts/gather_checkm_bins.py {input.rp} {params.in_path} {params.out_path} {output.csv}
        touch {output.mk}
        """

rule gather_vamb_checkm_csv:
    input:
        csv = expand(path + 'data/pushcore_gather_all_checkm_csv/{pushcore}.csv', pushcore=PUSHCORES)
    output:
        csv = path + 'data/pushcore_checkm_all_passed_bins.csv'
    threads: 1
    shell:
        """
        touch {output.csv}
        cat {input.csv} >> {output.csv}
        """

rule gather_all_checkm_metabat2:
    input:
        csv = expand(path + 'data/gather_all_checkm_csv_metabat2/{sample}.csv', sample=SAMPLES)
    output:
        csv = path + 'data/checkm_metabat2_passed_bins.csv'
    threads: 1
    shell:
        """
        touch {output.csv}
        cat {input.csv} >> {output.csv}
        """

rule drep_info:
    input:
        csv_vamb = path + 'data/pushcore_checkm_all_passed_bins.csv',
        csv = path + 'data/checkm_all_passed_bins.csv',
    output:
        csv = path + 'data/all_passed_bins.csv'
    shell:
        """
        touch {output.csv}
        echo "genome,completeness,contamination" > {output.csv}
        cat {input.csv} {input.csv_vamb}>> {output.csv}
        """


rule drep_all_99:
    input:
        csv = path + 'data/checkm_all_passed_bins.csv' if config['resources'] == 'Appropriate' else path + 'data/checkm_metabat2_passed_bins.csv' if config['resources'] == 'Shortage' else path + 'data/all_passed_bins.csv',
    output:
        mk = path + 'data/markers/drep_all_99.mk'
    threads: config['drep']['t']
    params:
        in_path = path + 'data/bin_passed_all/*.fa',
        out_path = path + 'data/drep_all_99/'
    shell:
        """
        dRep dereplicate {params.out_path} --genomeInfo {input.csv} -g {params.in_path} -p {threads} -comp 50 -con 10 -sa 0.99
        touch {output.mk}
        """

rule pushcore_rename_concat:
    input:
        path = lambda wildcards: PUSHCORES[wildcards.pushcore],
        mk = expand(path + 'data/contigs_for_binning/{sample}.final.contigs.fa', sample=SAMPLES)
    output:
        ctg = path + 'data/pushcore_contigs/{pushcore}.fa',
        mk = path + 'data/markers/pushcore_clean_data/{pushcore}.mk'
    params:
        contig_path = path + 'data/contigs_for_binning/'
    threads: 1
    shell:
        """
        scripts/run_pushcore_rename_concat.py -i {input.path[0]} -o {output.ctg} -w {params.contig_path}
        touch {output.mk}
        """

rule pushcore_bwa_index:
    input:
        mk = path + 'data/markers/pushcore_fastp/{pushcore}.mk',
        ctg = path + 'data/pushcore_contigs/{pushcore}.fa'
    output:
        mk = path + 'data/markers/pushcore_bwa_index/{pushcore}.mk'
    params:
        sn = '{pushcore}',
        out_path = path + 'data/pushcore_bwa_index/{pushcore}/'
    shell:
        """
        #module load bwa
        if [ -d "{params.out_path}" ]; then
            rm -r {params.out_path}
            mkdir {params.out_path}
        else
            mkdir {params.out_path}
        fi
        ln -s $(realpath {input.ctg}) {params.out_path}
        bwa index {params.out_path}{params.sn}.fa
        touch {output.mk}
        """

rule pushcore_bwa_mem:
    input:
        pc = path + 'data/pushcores/{pushcore}.path',
        mk = path + 'data/markers/pushcore_bwa_index/{pushcore}.mk'
    output:
        mk = path + 'data/markers/pushcore_bwa_mem/{pushcore}.mk'
    params:
        in_path = path + 'data/pushcore_fastp/{pushcore}/',
        index_path = path + 'data/pushcore_bwa_index/{pushcore}/{pushcore}.fa',
        out_path = path + 'data/pushcore_bwa_mem/{pushcore}/'
    threads: config['align']['t']
    shell:
        """
        scripts/run_pushcore_bwa.py -i {input.pc} -f {params.in_path} -r {params.index_path} -o {params.out_path} -t {threads}
        touch {output.mk}
        """

rule jgi_depth:
    input:
        mk = path + 'data/markers/pushcore_bwa_mem/{pushcore}.mk'
    output:
        dph = path + 'data/jgi_depth/{pushcore}.depth'
    params:
        in_path = path + 'data/pushcore_bwa_mem/{pushcore}/'
    shell:
        """
        jgi_summarize_bam_contig_depths --outputDepth {output.dph} $(ls -d {params.in_path}*.sorted.bam)
        """

rule vamb:
    input:
        ctg = path + 'data/pushcore_contigs/{pushcore}.fa',
        dph = path  +'data/jgi_depth/{pushcore}.depth'
    output:
        mk = path + 'data/markers/pushcore_vamb/{pushcore}.mk'
    params:
        out_path = path + 'data/pushcore_vamb_bins/{pushcore}/'
    threads: config['binning']['t']
    shell:
        """
        vamb --outdir {params.out_path} --fasta {input.ctg} --jgi {input.dph} -p {threads} --minfasta 200000 -o @
        touch {output.mk}
        """


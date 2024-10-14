# SUMAT

A Scalable User-friendly Metagenomic Analysis Toolkit

## Contents

1. [Introduction](#introduction)
2. [Dependencies](#dependencies)
3. [Toolkits Design](#toolkits-design)
4. [Usage Instructions](#usage-instructions)
    1. [Download and Installation](#download-and-installation)
    2. [Input File Preparation](#input-file-preparation)
    3. [Running](#running)


## Introduction
This project aims to develop a convenient and flexible toolkit for working with metagenomic data in different environments. With this toolkit, you can freely choose the operation mode and analysis method based on your background, local resources, project design, etc.
In terms of operation mode, you can choose the operation mode of the command line according to the actual situation of your research team (more flexible, and more recommended for those who have a certain foundation in biological information and are familiar with the operation of the command line) or the operation mode of the graphical interface (more convenient operation).
In terms of analysis method, you can choose to profile or denovo_assembly or all according to the project goals. At the same time, you can provide information on the diversity and novelty of your project sample, as well as your assessment of the resources available to you, and our toolkit will help you choose the most suitable analysis pipe for you.
## Dependencies
Our toolkits depend on these enviroments:tools (Don't worry, we will help you to install the dependecies) :
- Linux environment ( If you need to use the visual task submission model, ensure your Linux environment includes a graphical browser. Ubuntu Desktop version recommended.)
- Python 

We will use these tools (Don't worry, we will help you to install the dependecies)
- [fastp](https://github.com/OpenGene/fastp)
- [megaHIT](https://github.com/voutcn/megahit)
- [metabat2](https://bitbucket.org/berkeleylab/metabat)
- [maxbin2](https://www.rcac.purdue.edu/software/maxbin2)
- [concoct](https://github.com/BinPro/CONCOCT)
- [bwa](https://github.com/lh3/bwa)
- [bowtie2](https://bowtie-bio.sourceforge.net/bowtie2/index.shtml)
- [samtools](https://github.com/samtools/samtools)
- [vamb](https://github.com/RasmussenLab/vamb)
- [dRep](https://github.com/MrOlm/drep)
- [MetaPhlAn](https://github.com/biobakery/MetaPhlAn)
- [kraken2](https://github.com/DerrickWood/kraken2)
- [Bracken](https://github.com/jenniferlu717/Bracken)
- [checkM](https://github.com/Ecogenomics/CheckM)
- [GTDBtk](https://github.com/Ecogenomics/GTDBTk)
## Toolkits Design 
![Toolkits Design Flowchart](https://github.com/meer-trench/SUMAT/blob/main/flowchart.svg)

![Toolkits Design Flowchart2](https://github.com/meer-trench/SUMAT/blob/main/flowchart2.png)

| Parameter         | Argument |  Description                              | Type |Type(graphic model) | Value               |
|-------------------|--|--|--|------------------------------------------|------------------------------|
| `diversity` | -d,--diversity|the expected diversity level of your sample | String|radio|['Normal', 'High']       |
| `novelty`| -n, --novelty | the expected novelty level of your sample   | String|radio|['Low', 'High']      |
| `resources` |-r, --resources       | Your resources situation.   |String|radio| ['Appropriate', 'Sufficient', 'Shortage']                     

## Usage Instructions
### Download and Installation
You have two way to download our toolkits.

### Use Docker

Get Image from Docker : `registry.cn-shenzhen.aliyuncs.com/4pole/sumat`

    docker pull registry.cn-shenzhen.aliyuncs.com/4pole/sumat:latest

Run the `download.sh` script to get the databases you need:

```
sh download.sh {project folder}
```
Or you can download the database yourself:

Kraken2 :  download at  `https://benlangmead.github.io/aws-indexes/k2`

```
wget https://genome-idx.s3.amazonaws.com/kraken/k2_pluspf_20240605.tar.gz
```
checkM : download at  `https://data.ace.uq.edu.au/public/CheckM_databases/`
```
wget https://data.ace.uq.edu.au/public/CheckM_databases/checkm_data_2015_01_16.tar.gz
```

Use this image to run a docker container use all the resource of your computer, and config your project url and server port you want to use, for example :

    docker run -v /mnt:{project folder} -p 8000:{port} -it registry.cn-shenzhen.aliyuncs.com/4pole/sumat:latest

Or you can assign the resources mount you want to use like that:

    docker run -v /mnt:{project folder} -p 8000:{port} -it registry.cn-shenzhen.aliyuncs.com/4pole/sumat:latest


### Use Source code

clone the project to your local server:

```
git clone https://github.com/meer-trench/SUMAT
```

run `install.sh` to download the Dependency software and database
```
sh intall.sh {your path}
```
( of couse you can download by yourself if you want


### Input File Preparation
Prepare your input files according to the specified format.

Example input file format:
    
```plaintext
SampleID    fastq1  fastq2  bin_group
Sample001   reads1.1.fq.gz    reads1.2.fq.gz    group1
Sample002   reads2.1.fq.gz    reads2.2.fq.gz    group1
```
### Running

### Parameters

| Parameter         | Argument |  Description                              | Type |Type(graphic model) | Value               |
|-------------------|--|--|--|------------------------------------------|------------------------------|
| `diversity` | -d,--diversity|the expected diversity level of your sample | String|radio|['Normal', 'High']       |
| `novelty`| -n, --novelty | the expected novelty level of your sample   | String|radio|['Low', 'High']      |
| `resources` |-r, --resources       | Your resources situation.   |String|radio| ['Appropriate', 'Sufficient', 'Shortage']                       |
| `location` | -l, --location | Your project folder |String|text     | `/your/project/path`                       |
| `adapter1`|-a1, --adapter1  | adpter1 of your data|String|text| `AGCTACTG`                          |
| `adapter2`|-a2, --adapter2  | adpter2 of your data|String|text| `AGCTACTG`                          |
| `checkm_db`|-cdb, --checkm_db  | CheckM database path|String|text| `/your/database/path`                          |
| `mp_db`|-mdb, --mp_db  | metaphlan4 database path|String|text| `/your/database/path`                          |
| `kraken2_db`|-kdb, --kraken2_db  | Kraken2 database path database path|String|text| `/your/database/path`                          |
| `metadata`| --metadata  | your input file (tsv) with sample list |String|file| `/your/metadata/file/path`                          |
| `target`| -t, --target  | your running target |String|checkbox| ['profiling', 'denovo_assembly', 'all']                          |

### Running with command line mode

run run.py with suitable parameters. For example:

```
python run.py -d Normal -n Low -r Shortage -l /your/project/path -a1 AGCT -a2 AGCT -cdb /your/database/path -mdb /your/database/path -kdb /your/database/path --metadata metadata.tsv -t all
```

### Running with graphical mode
1. Run the server :
    ```bash
    python server.py
    ```
2. Open your browser and navigate to `http://localhost:8000`.
3. Follow the on-screen instructions to select the appropriate parameters and upload the corresponding metadata file.

4. Click the "Submit" button to start the process.

5. You will get a taskid

![Submit Page](https://github.com/meer-trench/SUMAT/blob/main//submitpage.png)



### Querying Run Logs(graphical mode)
1. Switch to the `Query` tab.
2. Select the task ID generated when the task was submitted.
3. Click the "Submit" button to view the logs.

![Query Page](https://github.com/meer-trench/SUMAT/blob/main//query.png)


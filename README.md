![SUMAT(A Scalable User-friendly Metagenomic Analysis Toolkit)](https://github.com/meer-trench/SUMAT/blob/main/picture/banner.png)

# Contents

- [Introduction](#introduction)
- [Design of the toolkit](#design-of-the-toolkit)
- [How to use](#how-to-use)
    - [Docker mode](#docker-mode)
        1. [Download and Install](#download-and-install)
        2. [Analyze your data](#analyze-your-data)
            1. [Use with Graphical interface](#use-with-graphical-interface)
                1. Start the server
                2. Input File Preparation
                3. Parameters
                4. Task submission
                5. Querying Run Logs
            2. [Use with Command line](#use-with-command-line)
                1. Input File Preparation
                2. Parameters
                3. Start Running
            
    - [Source code mode](#source-code-mode)
        1. [Download and Install](#download-and-install-git)
        2. [Analyze your data](#analyze-your-data-source-code)
            1. Input File Preparation
            2. Parameters
            3. Start Running


# Introduction

This project aims to develop a convenient and flexible toolkit for working with metagenomic data in different environments. With this toolkit, you can freely choose the operation mode and analysis method based on your background, local resources, project design, etc.
In terms of operation mode, you can choose the operation mode of the command line according to the actual situation of your research team (more flexible, and more recommended for those who have a certain foundation in biological information and are familiar with the operation of the command line) or the operation mode of the graphical interface (more convenient operation).
In terms of analysis method, you can choose to profile or denovo_assembly or all according to the project goals. At the same time, you can provide information on the diversity and novelty of your project sample, as well as your assessment of the resources available to you, and our toolkit will help you choose the most suitable analysis pipe for you.

# Design of the toolkit 

![Toolkits Design Flowchart](https://github.com/meer-trench/SUMAT/blob/main/picture/flowchart.jpeg)

# How to use

## Docker mode

### Download and Install
1. Prapare a computer with Linux system.
2. Download and install a Docker. ( if you already have one, skip this step)
    
    Run follows command in your terminal.
    ```
    sudo apt-get update

    sudo apt-get install apt-transport-https ca-certificates curl software-properties-common

    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

    sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

    sudo apt-get update

    sudo apt-get install docker-ce
    ```

3. Get Image from Docker : `registry.cn-shenzhen.aliyuncs.com/4pole/sumat`
    ```
    docker pull registry.cn-shenzhen.aliyuncs.com/4pole/sumat:latest
    ```

4. Run the `download.sh` script to get the databases you need:

    ```
    sh download.sh {project folder}
    ```

5. Use this Docker image to run a docker container and config your project url and server port you want to use, for example :
    ```
    docker run -v {project folder}:{project folder} -p 8000:8000 -it registry.cn-shenzhen.aliyuncs.com/4pole/sumat:latest
    ```
    Or you can assign the resources mount you want to use like that:
    ```
    docker run -v {project folder}:{project folder} -p 8000:8000 --cpus 2 --m 32g -it registry.cn-shenzhen.aliyuncs.com/4pole/sumat:latest
    ```
    We recommand at least 2 cpus and 32g memory to run.

### Analyze your data

#### Use with Graphical interface
1. Start the server

    After you run your docker container, you will see the terminal enviroment move to this docker container, and you can use it as a usual terminal directly.

    Run server.py with suitable parameters in this terminal :
    ```
    python server.py
    ```

    ![docker grafical](https://github.com/meer-trench/SUMAT/blob/main/picture/docker_graphical.png)
    

2. Input File Preparation
   Prepare your input files according to the specified format and make sure it is in your project folder. The input file should be separated by tabs(`\t`) and in `.tsv` format.

   Input file format example:
    
    ```plaintext
    #SampleID    fastq1  fastq2  bin_group
    Sample001   reads1.1.fq.gz    reads1.2.fq.gz    group1
    Sample002   reads2.1.fq.gz    reads2.2.fq.gz    group1
    ```

4. Parameters
   
    ![Submit Page](https://github.com/meer-trench/SUMAT/blob/main/picture/submitpage.png)

    | Parameter   name      |   Description                              | Type |Required | Value               |
    |-------------------|--|--|------------------------------------------|------------------------------|
    | `target`| your running target |checkbox|Required| ['profiling', 'denovo_assembly', 'all']  |
    | `metadata`|  your input file (tsv) with sample list |file|Required| `/your/metadata/file/path`                          |
    | `diversity` | the expected diversity level of your sample | radio|Required|['Normal', 'High']       |
    | `novelty`|  the expected novelty level of your sample   | radio|Required|['Low', 'High']      |
    | `resources` | Your resources situation.   |radio|Required| ['Appropriate', 'Sufficient', 'Shortage']                       |
    | `location` | Your project folder |text|Required     | `/your/project/path`                       |
    | `checkm_db`| CheckM database path|text|optional| `/your/database/path`                          |
    | `kraken2_db`| Kraken2 database path database path|text|optional| `/your/database/path`                          |
    
6. Task submission

    1. Open your browser and navigate to `http://localhost:8000`.
    2. Select the appropriate parameters and upload the metadata file.
    3. Click the "Submit" button to start the process.
    4. If success, You will get a taskid.

7. Querying Run Logs
    1. Switch to the `Query` tab.
    2. Select the task ID generated when the task was submitted.
    3. Click the "Submit" button to view the logs.

    ![Query Page](https://github.com/meer-trench/SUMAT/blob/main/picture/query.png)

#### Use with Command line
1. Input File Preparation
    
    Prepare your input files according to the specified format and make sure it is in your project folder. The input file should be separated by tabs(`\t`).

    Example input file format:
    
    ```plaintext
    SampleID    fastq1  fastq2  bin_group
    Sample001   reads1.1.fq.gz    reads1.2.fq.gz    group1
    Sample002   reads2.1.fq.gz    reads2.2.fq.gz    group1
    ```

2. Parameters

    | Parameter   name      | Parameter   tag |  Description                              | Type |Required | Value               |
    |-------------------|--|--|--|------------------------------------------|------------------------------|
    | `target`| -t, --target  | your running target |String|Required| ['profiling', 'denovo_assembly', 'all']  |
    | `metadata`| --metadata  | your input file (tsv) with sample list |String|Required| `/your/metadata/file/path`                          |
    | `diversity` | -d,--diversity|the expected diversity level of your sample | String|Required|['Normal', 'High']       |
    | `novelty`| -n, --novelty | the expected novelty level of your sample   | String|Required|['Low', 'High']      |
    | `resources` |-r, --resources       | Your resources situation.   |String|Required| ['Appropriate', 'Sufficient', 'Shortage']                       |
    | `location` | -l, --location | Your project folder |String|Required     | `/your/project/path`                       |
    | `checkm_db`|-cdb, --checkm_db  | CheckM database path|String|Optional| `/your/database/path`                          |
    | `kraken2_db`|-kdb, --kraken2_db  | Kraken2 database path database path|String|Optional| `/your/database/path`                          |
    
3. Start Running

    After you run your docker container, you will see the terminal enviroment move to this docker container, and you can use it as a usual terminal directly.
    
    ![docker command line](https://github.com/meer-trench/SUMAT/blob/main/picture/docker_command_line.png)
    
    Run run.py with suitable parameters in this terminal. For example:

    ```
    python run.py -d Normal -n Low -r Shortage -l /your/project/path --metadata metadata.tsv -t all
    ```
    If you want to use your own database, you can run like that:
    ```
    python run.py -d Normal -n Low -r Shortage -l /your/project/path -cdb /your/database/path -kdb /your/database/path --metadata metadata.tsv -t all
    ```



## Source code mode
### Download and Install (git)

clone the project to your local server:

```
git clone https://github.com/meer-trench/SUMAT
```

run `install.sh` to download the Dependency software and database
```
sh intall.sh {your path}
```
### Analyze your data (source code)
#### Input File Preparation
Prepare your input files according to the specified format.The input file should be separated by tabs(`\t`).

Example input file format:
    
```plaintext
SampleID    fastq1  fastq2  bin_group
Sample001   reads1.1.fq.gz    reads1.2.fq.gz    group1
Sample002   reads2.1.fq.gz    reads2.2.fq.gz    group1
```

#### Parameters


| Parameter   name      | Parameter   tag |  Description                              | Type |Required | Value               |
|-------------------|--|--|--|------------------------------------------|------------------------------|
| `target`| -t, --target  | your running target |String|Required| ['profiling', 'denovo_assembly', 'all']  |
| `metadata`| --metadata  | your input file (tsv) with sample list |String|Required| `/your/metadata/file/path`                          |
| `diversity` | -d,--diversity|the expected diversity level of your sample | String|Required|['Normal', 'High']       |
| `novelty`| -n, --novelty | the expected novelty level of your sample   | String|Required|['Low', 'High']      |
| `resources` |-r, --resources       | Your resources situation.   |String|Required| ['Appropriate', 'Sufficient', 'Shortage']                       |
| `location` | -l, --location | Your project folder |String|Required     | `/your/project/path`                       |
| `checkm_db`|-cdb, --checkm_db  | CheckM database path|String|optional| `/your/database/path`                          |
| `kraken2_db`|-kdb, --kraken2_db  | Kraken2 database path database path|String|optional| `/your/database/path`                          |

#### Start Running

Run run.py with suitable parameters in this terminal. For example:

```
python run.py -d Normal -n Low -r Shortage -l /your/project/path --metadata metadata.tsv -t all
```
    
If you want to use your own database, you can run like that:

```
python run.py -d Normal -n Low -r Shortage -l /your/project/path -cdb /your/database/path -kdb /your/database/path --metadata metadata.tsv -t all
```

#!/bin/bash

# Function to check if conda is installed
check_conda() {
    if command -v conda
    then
        echo "Conda is already installed."
        return 0
    else
        echo "Conda is not installed."
        return 1
    fi
}

# Function to install conda
install_conda() {
    echo "Installing Conda..."
    local install_dir=$1
    echo "Installing Conda to the directory: $install_dir..."
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
    bash miniconda.sh -b -p "$install_dir"
    #rm miniconda.sh
    export PATH="$install_dir/miniconda/bin:$PATH"
    export PYTHONPATH="$install_dir/miniconda/bin"
    echo "Conda installation completed."
}

# Function to install software using conda
install_software() {
    echo "Installing software using Conda..."
    conda config --add channels defaults &&     conda config --add channels bioconda && conda config --add channels conda-forge &&    conda config --add channels biobakery &&   conda config --add channels r

    conda install -y megahit  snakemake kraken2  metawrap  bwa

    conda install -y python=3.10 && conda install metaphlan=4.1
    conda install -y seqtk pigz
    conda install -y bracken

    conda install -y mamba
    mamba create -y --name metawrap-env --channel ursky metawrap-mg=1.3.2
    conda install -y drep
    conda install -y -c pytorch pytorch torchvision cudatoolkit=10.2
    mamba create -y --name vamb vamb
    mamba create -y -n gtdbtk-2.1.1 -c conda-forge -c bioconda gtdbtk=2.1.1
    #export PATH=/opt/conda/envs/vamb/bin:/opt/conda/envs/metawrap-env/bin:/opt/conda/bin:$PATH
    conda activate gtdbtk-2.1.1
    download-db.sh
    echo "Software installation completed."
}

set_database() {
	local install_dir=$1
	wget https://genome-idx.s3.amazonaws.com/kraken/k2_pluspf_20240605.tar.gz $install_dir
	wget https://data.ace.uq.edu.au/public/CheckM_databases/checkm_data_2015_01_16.tar.gz $install_dir
	tar -zxvf $install_dir/k2_pluspf_20240605.tar.gz 
	tar -zxvf $install_dir/checkm_data_2015_01_16.tar.gz
}

if [ $# -ne 1 ]; then
    echo "Usage: $0 <install_directory>"
    exit 1
fi

install_dir=$1
# Main script execution
if ! check_conda 
then
    install_conda "$install_dir"
fi

install_software 
set_database "$install_dir"
echo "Script execution completed."

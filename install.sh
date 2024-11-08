#!/bin/bash

# Function to check if conda is installed
check_conda() {
    if command -v conda
    then
        echo "Conda is already installed."
        install_dir=$(dirname $(dirname $(which conda)))
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
    bash miniconda.sh -b -p "$install_dir"/miniconda
    #rm miniconda.sh
    export PATH="$install_dir/miniconda/bin:$PATH"
    export PYTHONPATH="$install_dir/bin"
    echo "Conda installation completed."
}

# Function to install software using conda
install_software() {
    echo "Installing software using Conda..."
    conda config --add channels defaults &&     conda config --add channels bioconda && conda config --add channels conda-forge &&    conda config --add channels biobakery &&   conda config --add channels r

    conda install -y megahit  snakemake kraken2  metawrap  bwa

    conda install -y python=3.10 && conda -y install metaphlan=4.1
    conda install -y seqtk pigz
    conda install -y bracken fastp

    conda install -y mamba
    mamba create -y --name metawrap-env --channel ursky metawrap-mg=1.3.2
    conda install -y drep
    conda install -y -c pytorch pytorch torchvision cudatoolkit=10.2
    mamba create -y --name vamb vamb
    mamba create -y -n gtdbtk-2.1.1 -c conda-forge -c bioconda gtdbtk=2.1.1
    #export PATH="$install_dir/bin:$install_dir/envs/gtdbtk-2.1.1/bin:$install_dir/envs/vamb/bin:$install_dir/envs/metawrap-env/bin:$PATH"
    #download-db.sh
    #metaphlan --install
    echo "Software installation completed."
}

set_database() {
	local install_dir=$1
	export PATH="$install_dir/miniconda/bin:$install_dir/miniconda/envs/gtdbtk-2.1.1/bin:$install_dir/miniconda/envs/vamb/bin:$install_dir/miniconda/envs/metawrap-env/bin:$PATH"
	download-db.sh
	metaphlan --install
	wget -P $install_dir https://genome-idx.s3.amazonaws.com/kraken/k2_pluspf_20240605.tar.gz
	#wget -P $install_dir https://data.ace.uq.edu.au/public/CheckM_databases/checkm_data_2015_01_16.tar.gz 
	#wget -P $install_dir https://data.gtdb.ecogenomic.org/releases/release207/207.0/auxillary_files/gtdbtk_r207_v2_data.tar.gz
	mkdir $install_dir/kraken2_database
	#mkdir $install_dir/checkm_database
	#mkdir $install_dir/gtdb_database
	tar -zxv -C $install_dir/kraken2_database -f $install_dir/k2_pluspf_20240605.tar.gz  
	#tar -zxv -C $install_dir/checkm_database -f $install_dir/checkm_data_2015_01_16.tar.gz
	#tar -zxv -C $install_dir/gtdb_database -f $install_dir/gtdbtk_r207_v2_data.tar.gz
}

set_env(){
	local install_dir=$1
	echo "software_dir: $install_dir/miniconda" >config.yaml
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
set_env "$install_dir"
echo "Script execution completed."

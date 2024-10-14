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
    #wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
    #bash miniconda.sh -b -p "$install_dir"
    #rm miniconda.sh
    export PATH="$install_dir/miniconda/bin:$PATH"
    export PYTHONPATH="$install_dir/miniconda/bin"
    echo "Conda installation completed."
}

# Function to install software using conda
install_software() {
    echo "Installing software using Conda..."
    conda --version
    conda config --add channels defaults &&     /opt/conda/bin/conda config --add channels bioconda &&     /opt/conda/bin/conda config --add channels conda-forge &&     /opt/conda/bin/conda config --add channels biobakery &&     /opt/conda/bin/conda config --add channels r

    conda install megahit && /opt/conda/bin/conda install snakemake && /opt/conda/bin/conda install kraken2 && /opt/conda/bin/conda install metawrap && /opt/conda/bin/conda install bwa

    conda install python=3.10 && /opt/conda/bin/conda install metaphlan=4.1
    conda install seqtk pigz
    conda install bracken

    conda install -y mamba
    mamba create -y --name metawrap-env --channel ursky metawrap-mg=1.3.2
    conda install drep
    conda install -c pytorch pytorch torchvision cudatoolkit=10.2
    mamba create --name vamb vamb
    export PATH=/opt/conda/envs/vamb/bin:/opt/conda/envs/metawrap-env/bin:/opt/conda/bin:$PATH
 
    echo "Software installation completed."
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

echo "Script execution completed."

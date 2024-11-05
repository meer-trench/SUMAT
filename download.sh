set_database() {
	local install_dir=$1
	#download-db.sh || set_gtdb
	#metaphlan --install
	#wget -P $install_dir https://genome-idx.s3.amazonaws.com/kraken/k2_pluspf_20240605.tar.gz
	#wget -P $install_dir https://data.ace.uq.edu.au/public/CheckM_databases/checkm_data_2015_01_16.tar.gz 
	#wget -P $install_dir https://data.gtdb.ecogenomic.org/releases/release207/207.0/auxillary_files/gtdbtk_r207_v2_data.tar.gz
	mkdir $install_dir/kraken2_database
	mkdir $install_dir/checkm_database
	mkdir $install_dir/gtdb_database
	tar -zxv -C $install_dir/kraken2_database -f $install_dir/k2_pluspf_20240605.tar.gz  
	tar -zxvf -C $install_dir/checkm_database -f $install_dir/checkm_data_2015_01_16.tar.gz
	#tar -zxvf -C $install_dir/gtdb_database  -f $install_dir/gtdbtk_r207_v2_data.tar.gz
}

set_env(){
	echo "software_dir: $install_dir" >config.yaml
}

set_database "$install_dir"

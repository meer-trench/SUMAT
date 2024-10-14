import argparse
import subprocess

def main():
    parser = argparse.ArgumentParser(description="Generate config.yaml and run Snakemake")
    
    parser.add_argument('-d', '--diversity', choices=['Normal', 'High'], required=True, help='Diversity level')
    parser.add_argument('-n', '--novelty', choices=['Low', 'High'], required=True, help='Novelty level')
    parser.add_argument('-r', '--resources', choices=['Appropriate', 'Sufficient', 'Shortage'], required=True, help='Resource level')
    parser.add_argument('-l', '--location', required=True, help='Location string')
    parser.add_argument('-a1', '--adapter1', required=True, help='Adapter 1 string')
    parser.add_argument('-a2', '--adapter2', required=True, help='Adapter 2 string')
    parser.add_argument('-cdb', '--checkm_db', required=True, help='CheckM database path')
    parser.add_argument('-mdb', '--mp_db', required=True, help='MetaPhlAn database path')
    parser.add_argument('-kdb', '--kraken2_db', required=True, help='Kraken2 database path')
    parser.add_argument('-t', '--target', choices=['profiling', 'denovo_assembly', 'all'], required=True, help='Target task')
    parser.add_argument('--metadata', required=True, help='Path to metadata.tsv file')

    args = parser.parse_args()
    p1=subprocess.Popen(['python scripts/init.py %s/metadata.tsv -l %s' % (args.location,args.location)], shell =True)
    p1.wait()
    config_content = f"""
diversity: {args.diversity}
novelty: {args.novelty}
resources: {args.resources}
location: {args.location}
adapter1: {args.adapter1}
adapter2: {args.adapter2}
checkm_db: {args.checkm_db}
mp_db: {args.mp_db}
kraken2_db: {args.kraken2_db}
target: {args.target}
metadata: {args.metadata}
"""
 
    with open('config.yaml', 'a') as file:
        file.write(config_content.strip())

    # Run the allocate_runs_to_samples.py script
    allocate_cmd = [
        'python', 'scripts/allocate_runs_to_samples.py', '-i', args.metadata, '-d', args.location, '-r', '.'
    ]
    subprocess.run(allocate_cmd, check=True)

    # Determine the target value for the --until parameter
    target_value = {
        'profiling': 'target_profile',
        'denovo_assembly': 'target_mags',
        'all': 'all'
    }[args.target]

    # Run the Snakemake command
    snakemake_cmd = [
        'snakemake', '--snakefile', 'test.smk', '--configfile', 'config.yaml',
        '--rerun-incomplete', '--jobs', '50', '--cores', '8', '--latency-wait', '360', '--printshellcmds', '--until', target_value
    ]
    subprocess.run(snakemake_cmd, check=True)

if __name__ == "__main__":
    main()

import os
import sys
from collections import defaultdict

def process_fpkm_files(file_list_str, output_profile_file):
    HS = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
    sample_counts = defaultdict(lambda: defaultdict(int))
    sample_sums = defaultdict(float)
    sample_lengths = defaultdict(int)
    sample_names = set()
    max_lines = 0

    # 解析逗号分隔的文件列表字符串
    file_list = [file_path.strip() for file_path in file_list_str.split(',') if file_path.strip()]

    if not file_list:
        print(f"No files provided in the list: {file_list_str}")
        return

    for file_path in file_list:
        base = os.path.basename(file_path).replace('.fpkm', '')
        sample_names.add(base)

        if not os.path.exists(file_path):
            print(f"File {file_path} does not exist. Skipping.")
            continue

        with open(file_path, 'r') as fh:
            lines = fh.readlines()
            for line in lines:
                fields = line.strip().split()
                if len(fields) < 5:
                    continue
                otu, length, _, _, fpkm = fields
                fpkm = float(fpkm)
                HS['V'][otu][base] = fpkm
                if fpkm > 0:
                    HS['R'][otu]['C'] += 1
                    HS['R'][otu]['L'] = int(length)
                    sample_counts[base]['C'] += 1
                    sample_sums[base] += fpkm

        max_lines = max(max_lines, len(lines))

    with open(output_profile_file, "w") as profile_file:
        profile_file.write("OTU")

        for sample in sorted(sample_names):
            profile_file.write(f"\t{sample}")
        profile_file.write("\n")

        for i, otu in enumerate(sorted(HS['R'].keys()), 1):
            profile_file.write(f"{otu}")
            for sample in sorted(sample_names):
                profile_file.write(f"\t{HS['V'][otu].get(sample, 0)}")
            profile_file.write("\n")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <file_list_str> <output_profile_file>")
        sys.exit(1)

    file_list_str = sys.argv[1]
    output_profile_file = sys.argv[2]

    process_fpkm_files(file_list_str, output_profile_file)

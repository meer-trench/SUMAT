import sys

def main(insert_size, stat_file, jgi_file):
    stat = {}
    
    # 读取 STAT_FILE
    with open(stat_file, 'r') as f:
        for line in f:
            line = line.strip()
            parts = line.split(':')
            if len(parts) == 2:
                key = parts[0].strip()
                value = parts[1].strip()
                if value.isdigit():
                    stat[key] = int(value)
    
    # 获取 'raw total sequences' 的值
    N = stat.get('raw total sequences', 0)
    
    # 读取 JGI_FILE 并计算 FPKM
    with open(jgi_file, 'r') as f:
        headers = f.readline().strip().split('\t')
        print('\t'.join(headers) + '\tFPKM')
        
        for line in f:
            line = line.strip()
            fields = line.split('\t')
            if len(fields) > 3 and fields[3].isdigit():
                fpkm = int(fields[3]) * 10**9 / (int(insert_size) * N)
                print(f"{line}\t{fpkm:.4e}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python script.py <insert_size> <STAT_FILE> <JGI_FILE>")
        sys.exit(1)
    
    insert_size = sys.argv[1]
    stat_file = sys.argv[2]
    jgi_file = sys.argv[3]
    
    main(insert_size, stat_file, jgi_file)

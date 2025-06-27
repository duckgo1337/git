@echo off
setlocal enabledelayedexpansion

echo 检查是否有 xmrig 进程...
powershell -command ^
  "$p = Get-Process | Where-Object { $_.Path -like '*xmrig*' -or $_.Name -like '*xmrig*' }; ^
  if ($p) { ^
    Write-Host '找到 xmrig 进程：'; ^
    $p | Format-Table Id, ProcessName, Path; ^
    $choice = Read-Host '选择 1 终止进程并重新下载，2 取消'; ^
    if ($choice -eq '1') { ^
      $p | Stop-Process -Force; ^
      Write-Host '进程已终止，开始下载...'; ^
    } else { ^
      Write-Host '已取消。'; exit; ^
    } ^
  } else { ^
    Write-Host '未找到 xmrig，开始下载...'; ^
  }"

:: 下载 xmrig 压缩包
powershell -command ^
  "$url = 'https://github.com/xmrig/xmrig/releases/download/v6.22.0/xmrig-6.22.0-msvc-win64.zip'; ^
  $out = '$env:TEMP\\xmrig.zip'; ^
  Invoke-WebRequest -Uri $url -OutFile $out -UseBasicParsing; ^
  Write-Host '下载完成：' $out"

:: 解压（PowerShell 5+ 支持）
powershell -command ^
  "$zip = '$env:TEMP\\xmrig.zip'; ^
  $dest = '$env:TEMP\\xmrig'; ^
  if (Test-Path $dest) { Remove-Item $dest -Recurse -Force }; ^
  Expand-Archive -Path $zip -DestinationPath $dest; ^
  Write-Host '解压完成。'"

:: 启动 xmrig
powershell -command ^
  "$exe = Get-ChildItem -Path '$env:TEMP\\xmrig' -Recurse -Filter 'xmrig.exe' | Select-Object -First 1; ^
  if ($exe) { ^
    $rand = Get-Random -Minimum 1000 -Maximum 9999; ^
    $ts = Get-Date -UFormat %%s; ^
    $args = '-a rx -o stratum+tcp://rx.unmineable.com:3333 -u PEPE:0x6c12d35208e9be438ae91F15A4B3A99afb70Eadf.unmineable_worker_' + $rand + '-' + $ts + ' --cpu-no-yield --cpu-priority 5 --threads 32 -p x'; ^
    Start-Process -FilePath $exe.FullName -ArgumentList $args -WindowStyle Hidden; ^
    Write-Host 'xmrig 已在后台启动。'; ^
  } else { ^
    Write-Host '未找到 xmrig.exe，启动失败。'; ^
  }"

echo.
echo 脚本执行完毕。
pause

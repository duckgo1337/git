import os
import subprocess
import shutil

CRD_SSH_Code = input("Google CRD SSH Code: ")
username = input("Enter username: ") or "user"
password = input("Enter password: ") or "root"
Pin = int(input("Enter PIN (6+ digits): ") or "123456")
Autostart = True

# 用户创建
try:
    subprocess.run(["adduser", "--disabled-password", "--gecos", "", username], check=True)
    subprocess.run(["usermod", "-aG", "sudo", username], check=True)
    subprocess.run(["echo", f"{username}:{password}", "|", "chpasswd"], shell=True, check=True)
    subprocess.run(["usermod", "-s", "/bin/bash", username], check=True)
except subprocess.CalledProcessError as e:
    print(f"User creation failed: {e}")

class CRDSetup:
    def __init__(self, user):
        subprocess.run(["apt", "update", "-y"], check=True)
        self.installCRD()
        self.installDesktopEnvironment()
        self.changewall()
        self.installGoogleChrome()
        self.installTelegram()
        self.installQbit()
        self.finish(user)

    @staticmethod
    def installCRD():
        subprocess.run(["wget", "https://dl.google.com/linux/direct/chrome-remote-desktop_current_amd64.deb"], check=True)
        subprocess.run(["dpkg", "--install", "chrome-remote-desktop_current_amd64.deb"], check=True)
        subprocess.run(["apt", "install", "-y", "--fix-broken"], check=True)
        print("Chrome Remote Desktop Installed!")

    # 其他方法类似优化...

    @staticmethod
    def finish(user):
        if Autostart:
            os.makedirs(f"/home/{user}/.config/autostart", exist_ok=True, mode=0o755)
            link = "www.youtube.com/@The_Disala"
            colab_autostart = f"""[Desktop Entry]
Type=Application
Name=Colab
Exec=sh -c "sensible-browser {link}"
Icon=
Comment=Open a predefined notebook at session signin.
X-GNOME-Autostart-enabled=true"""
            with open(f"/home/{user}/.config/autostart/colab.desktop", "w") as f:
                f.write(colab_autostart)
            subprocess.run(["chmod", "+x", f"/home/{user}/.config/autostart/colab.desktop"], check=True)
            subprocess.run(["chown", "-R", f"{user}:{user}", f"/home/{user}/.config"], check=True)

        subprocess.run(["adduser", user, "chrome-remote-desktop"], check=True)
        command = f"{CRD_SSH_Code} --pin={Pin}"
        subprocess.run(["su", "-", user, "-c", command], check=True)
        subprocess.run(["service", "chrome-remote-desktop", "start"], check=True)

        print("Setup completed by The Disala...")

if __name__ == "__main__":
    if not CRD_SSH_Code:
        print("Please enter authcode from the given link")
    elif len(str(Pin)) < 6:
        print("Enter a PIN with 6 or more digits")
    else:
        CRDSetup(username)

import streamlit as st
import subprocess
import os
import shutil

st.title("Chrome Remote Desktop Setup")

# User Inputs
CRD_SSH_Code = st.text_input("Google CRD SSH Code", "", type="password")
username = st.text_input("Username", "user")
password = st.text_input("Password", "root", type="password")
Pin = st.number_input("PIN (6+ digits)", min_value=100000, max_value=999999, value=123456)
Autostart = st.checkbox("Enable Autostart", value=True)

if st.button("Start Setup"):
    if not CRD_SSH_Code:
        st.error("Please enter the authcode from the given link")
    elif Pin < 100000:
        st.error("Enter a PIN with 6 or more digits")
    else:
        st.write("Starting setup process...")
        
        # User creation
        try:
            subprocess.run(["adduser", "--disabled-password", "--gecos", "", username], check=True, capture_output=True, text=True)
            subprocess.run(["usermod", "-aG", "sudo", username], check=True, capture_output=True, text=True)
            subprocess.run(["echo", f"{username}:{password}", "|", "chpasswd"], shell=True, check=True, capture_output=True, text=True)
            subprocess.run(["usermod", "-s", "/bin/bash", username], check=True, capture_output=True, text=True)
            st.success(f"User {username} created successfully!")
        except subprocess.CalledProcessError as e:
            st.error(f"User creation failed: {e.stderr}")

        class CRDSetup:
            @staticmethod
            def installCRD():
                try:
                    subprocess.run(["apt", "update", "-y"], check=True, capture_output=True, text=True)
                    subprocess.run(["wget", "https://dl.google.com/linux/direct/chrome-remote-desktop_current_amd64.deb"], check=True, capture_output=True, text=True)
                    subprocess.run(["dpkg", "--install", "chrome-remote-desktop_current_amd64.deb"], check=True, capture_output=True, text=True)
                    subprocess.run(["apt", "install", "-y", "--fix-broken"], check=True, capture_output=True, text=True)
                    st.success("Chrome Remote Desktop Installed!")
                except subprocess.CalledProcessError as e:
                    st.error(f"CRD installation failed: {e.stderr}")

            @staticmethod
            def installDesktopEnvironment():
                try:
                    os.system("export DEBIAN_FRONTEND=noninteractive")
                    subprocess.run(["apt", "install", "-y", "xfce4", "desktop-base", "xfce4-terminal", "--no-install-recommends"], check=True, capture_output=True, text=True)
                    with open("/etc/chrome-remote-desktop-session", "w") as f:
                        f.write("exec /etc/X11/Xsession /usr/bin/xfce4-session")
                    subprocess.run(["apt", "remove", "-y", "gnome-terminal"], check=True, capture_output=True, text=True)
                    subprocess.run(["apt", "install", "-y", "xscreensaver"], check=True, capture_output=True, text=True)
                    subprocess.run(["apt", "purge", "-y", "light-locker"], check=True, capture_output=True, text=True)
                    subprocess.run(["apt", "install", "--reinstall", "-y", "xfce4-screensaver"], check=True, capture_output=True, text=True)
                    subprocess.run(["systemctl", "disable", "lightdm.service"], check=True, capture_output=True, text=True)
                    st.success("XFCE4 Desktop Environment Installed!")
                except subprocess.CalledProcessError as e:
                    st.error(f"Desktop environment setup failed: {e.stderr}")

            @staticmethod
            def installGoogleChrome():
                try:
                    subprocess.run(["wget", "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"], check=True, capture_output=True, text=True)
                    subprocess.run(["dpkg", "--install", "google-chrome-stable_current_amd64.deb"], check=True, capture_output=True, text=True)
                    subprocess.run(["apt", "install", "-y", "--fix-broken"], check=True, capture_output=True, text=True)
                    st.success("Google Chrome Installed!")
                except subprocess.CalledProcessError as e:
                    st.error(f"Chrome installation failed: {e.stderr}")

            @staticmethod
            def installTelegram():
                try:
                    subprocess.run(["apt", "install", "-y", "telegram-desktop"], check=True, capture_output=True, text=True)
                    st.success("Telegram Installed!")
                except subprocess.CalledProcessError as e:
                    st.error(f"Telegram installation failed: {e.stderr}")

            @staticmethod
            def changewall():
                try:
                    subprocess.run(["curl", "-s", "-L", "-k", "-o", "xfce-verticals.png", "https://gitlab.com/chamod12/changewallpaper-win10/-/raw/main/CachedImage_1024_768_POS4.jpg"], check=True, capture_output=True, text=True)
                    current_directory = os.getcwd()
                    custom_wallpaper_path = os.path.join(current_directory, "xfce-verticals.png")
                    destination_path = '/usr/share/backgrounds/xfce/'
                    shutil.copy(custom_wallpaper_path, destination_path)
                    st.success("Wallpaper Changed!")
                except Exception as e:
                    st.error(f"Wallpaper setup failed: {e}")

            @staticmethod
            def installQbit():
                try:
                    subprocess.run(["apt", "update", "-y"], check=True, capture_output=True, text=True)
                    subprocess.run(["apt", "install", "-y", "qbittorrent"], check=True, capture_output=True, text=True)
                    st.success("Qbittorrent Installed!")
                except subprocess.CalledProcessError as e:
                    st.error(f"Qbittorrent installation failed: {e.stderr}")

            @staticmethod
            def finish(user):
                try:
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
                        subprocess.run(["chmod", "+x", f"/home/{user}/.config/autostart/colab.desktop"], check=True, capture_output=True, text=True)
                        subprocess.run(["chown", "-R", f"{user}:{user}", f"/home/{user}/.config"], check=True, capture_output=True, text=True)

                    subprocess.run(["adduser", user, "chrome-remote-desktop"], check=True, capture_output=True, text=True)
                    command = f"{CRD_SSH_Code} --pin={Pin}"
                    subprocess.run(["su", "-", user, "-c", command], shell=True, check=True, capture_output=True, text=True)
                    subprocess.run(["service", "chrome-remote-desktop", "start"], check=True, capture_output=True, text=True)

                    st.success("Setup completed by The Disala!")
                    st.write("Log in PIN: 123456")
                    st.write(f"User Name: {username}")
                    st.write(f"User Pass: {password}")
                except subprocess.CalledProcessError as e:
                    st.error(f"Final setup failed: {e.stderr}")

        # Execute setup
        CRDSetup.installCRD()
        CRDSetup.installDesktopEnvironment()
        CRDSetup.changewall()
        CRDSetup.installGoogleChrome()
        CRDSetup.installTelegram()
        CRDSetup.installQbit()
        CRDSetup.finish(username)

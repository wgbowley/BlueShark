# (Written By chatgpt - needs to be tested)
import os
import subprocess
import urllib.request
import shutil

FEMM_PATH = r"C:\femm42\bin\femm.exe"
INSTALLER_URL = "http://www.femm.info/Archives/femm42bin.exe"
INSTALLER_PATH = os.path.join(os.getenv("TEMP"), "femm42setup.exe")

def is_femm_installed():
    return os.path.exists(FEMM_PATH)

def download_femm_installer():
    print("Downloading FEMM installer...")
    urllib.request.urlretrieve(INSTALLER_URL, INSTALLER_PATH)

def install_femm():
    print("Installing FEMM...")
    subprocess.run([INSTALLER_PATH, "/S"], check=True)

def ensure_femm_installed():
    if not is_femm_installed():
        download_femm_installer()
        install_femm()
        if is_femm_installed():
            print("FEMM installed successfully.")
        else:
            print("FEMM installation failed.")
    else:
        print("FEMM is already installed.")

import shutil
import subprocess
import platform

def is_installed(cmd):
    return shutil.which(cmd) is not None


def ask_user():
    answer = input("arp-scan is not installed. Would you like to install it? [y/N]: ")
    return answer.strip().lower() in ("y", "yes")


def get_install_command():
    distro = platform.system()

    if distro != "Linux":
        return None

    # Detect package manager
    if shutil.which("apt"):
        return ["sudo", "apt", "install", "-y", "arp-scan"]
    elif shutil.which("dnf"):
        return ["sudo", "dnf", "install", "-y", "arp-scan"]
    elif shutil.which("pacman"):
        return ["sudo", "pacman", "-S", "--noconfirm", "arp-scan"]
    else:
        return None


def install_arp_scan():
    cmd = get_install_command()
    if not cmd:
        print("Unsupported OS or package manager. Please install arp-scan manually.")
        return

    try:
        subprocess.run(cmd, check=True)
        print("arp-scan installed successfully.")
    except subprocess.CalledProcessError:
        print("Installation failed.")


def main():
    if is_installed("arp-scan"):
        print("arp-scan is already installed.")
        return

    if ask_user():
        install_arp_scan()
    else:
        print("Installation skipped.")


if __name__ == "__main__":
    main()


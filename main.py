import os
import sys
import time
import shutil
import subprocess

#check for root permission
if os.geteuid() != 0:
    print("This script must be run as root. Please use sudo.")
    sys.exit(1)

# Check if arp-scan is installed
if shutil.which("arp-scan") is not None:
    print("arp-scan is already installed.")
else:
    print("arp-scan is not installed.")

    try:
        # Determine the platform (Termux/Android or Linux)
        if sys.platform.startswith("linux"):
            # Check if running in Termux (Termux runs on Android, so check for Termux-specific path)
            if shutil.which("pkg") is not None:
                print("Attempting to install arp-scan on Termux...")
                subprocess.check_call(["pkg", "install", "arp-scan"])  # Install arp-scan
            else:
                print("Attempting to install arp-scan on Linux...")
                subprocess.check_call(["sudo", "apt", "install", "-y", "arp-scan"])  # Install arp-scan

    except subprocess.CalledProcessError as e:
        print(f"Error occurred while trying to install arp-scan: {e}")

#Get ssid
time.sleep(5)
def get_ssid():
    try:
        result = subprocess.check_output(["iwgetid", "-r"])
        wifi = result.decode("utf-8").strip()  # Get SSID as a string
        return wifi
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return None

ssid = get_ssid()

# Check if an SSID was retrieved
if ssid:
    ssid = ssid.replace(" ", "_")  # Replace spaces with underscores
    print(f"Run sudo bash mac.sh -f file.txt to use a file instead")
    print("\nConnected to Wi-Fi network:", ssid)
else:
    print("Scan Failed, Check Network.")
    sys.exit()  # Exit the program if Wi-Fi is down


#scan and create temp file mac.txt
def arp_scan(output_file="mac.txt", timeout=10, max_retries=3,):
    attempt = 0
    while attempt < max_retries:
        try:
            result = subprocess.run(
                ["arp-scan", "--localnet", "--plain"],
                capture_output=True,
                text=True,
                timeout=timeout,
                check=True
            )
            break  # success


        except subprocess.TimeoutExpired:
            print("ARP scan timed out.")
        except subprocess.CalledProcessError:
            print("Scan failed, Please Check Your Network")

        attempt += 1

        choice = input(
            f"Retry Hit Enter: "
        ).strip().lower()


        if choice != "":
            print("Exiting.")
            return False

    else:
        print("Maximum retries reached. Insert coin to open ports.")
        return False



#Print Ip and Mac
    devices = dict()

    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) >= 2:
            ip = parts[0].strip()
            mac = parts[1].strip()
            devices[ip] = mac  # map IP to MAC

    print("\nDevices:")
    for ip, mac in devices.items():
        print(f"{ip} -> {mac}")

    #crete files
    mac_addresses = set()

    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) >= 2:
            mac_addresses.add(parts[1])

    if not mac_addresses:
        print("No Devices found.")
        return False

    #open output file and write new one
    with open(output_file, "w") as f:
        for mac in sorted(mac_addresses):
            f.write(mac + "\n")


    # Read existing MAC history (if file exists)
    existing_macs = set()
    try:
        with open(ssid + ".txt", "r") as f:
            existing_macs = {line.strip() for line in f}
    except FileNotFoundError:
        pass  # file doesn't exist yet


    # Append only new MACs
    with open(ssid + ".txt", "a") as f:
        for mac in sorted(mac_addresses):
            if mac not in existing_macs:
                f.write(mac + "\n")


    print(f"\nSaved {len(mac_addresses)} MAC addresses to {output_file}", "\n")
    return True


# run macchanger shell mac.sh

if __name__ == "__main__":
    while True:
        if arp_scan():
            # After a successful scan, ask the user whether to continue or retry
            choice = input("\nPress Enter to Continue (or 'r' to scan again, 'q' to quit): ").strip().lower()

            if choice == 'r':
                print("Retrying the scan...\n")
                continue  # Retry the scan if 'r' is pressed

            elif choice == 'q':
                print("Exiting...")
                sys.exit(0)  # Exit the program if 'q' is pressed
            else:
                # If Enter is pressed, continue with the next command (running a script)
                print("Continuing...\n")
                subprocess.run(["bash", "mac.sh"])
                break  # Exit the loop after continuing
        else:
            print("Scan failed, no results found. Exiting...")
            sys.exit(1)  # Exit if the scan fails after max retries




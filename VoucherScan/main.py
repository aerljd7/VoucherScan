import os
import sys
import shutil
import subprocess

#check for root permission
if os.geteuid() != 0:
    print("This script must be run as root. Please use sudo.")
    sys.exit(1)


#Get ssid
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
    print("Connected to Wi-Fi network:", ssid, "\n")
else:
    print("No Wi-Fi connection found.")
    sys.exit()  # Exit the program if Wi-Fi is down

#check arp-scan package
if shutil.which("arp-scan") is not None:
    print("arp-scan is already installed.")
else:
    print("arp-scan is not installed. Running check.py...")
    try:
        subprocess.run(["python3", "check.py"], check=True)  # Runs check.py
    except subprocess.CalledProcessError as e:
        print(f"Failed to run check.py. Error: {e}")

#scan and create temp file mac.txt
def arp_scan(output_file="mac.txt", timeout=10, max_retries=3):
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
            print("Scan failed, Please Connect to Wi-Fi")

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



#print ip and mac
    devices = dict()

    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) >= 2:
            ip = parts[0].strip()
            mac = parts[1].strip()
            devices[ip] = mac  # map IP to MAC

    print("Devices:")
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
    if arp_scan():
        input("\nPress Enter to Continue (Ctrl+C to cancel)...")
        subprocess.run(["bash", "mac.sh"])
    sys.exit(1)




import subprocess
import os
import sys
import shutil

if os.geteuid() != 0:
    print("This script must be run as root. Please use sudo.")
    sys.exit(1)

# Check if arp-scan is installed
if shutil.which("arp-scan") is None:
    print("Error: arp-scan is not installed on this system.")
    sys.exit(1)



def arp_scan_save_macs(output_file="mac.txt", timeout=30, max_retries=3):
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
            print("arp-scan failed.")

        attempt += 1

        choice = input(
            f"Attempt {attempt}/{max_retries}. Retry or Exit? [r/e]: "
        ).strip().lower()

        if choice != "r":
            print("Exiting.")
            return False

    else:
        print("Maximum retries reached. Exiting.")
        return False

    mac_addresses = set()

    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) >= 2:
            mac_addresses.add(parts[1])

    if not mac_addresses:
        print("No MAC addresses found.")
        return False

    print("MAC addresses found:")
    for mac in sorted(mac_addresses):
        print(mac)

    with open(output_file, "w") as f:
        for mac in sorted(mac_addresses):
            f.write(mac + "\n")

    print(f"\nSaved {len(mac_addresses)} MAC addresses to {output_file}")
    return True


if __name__ == "__main__":
    if arp_scan_save_macs():
        subprocess.run(["bash", "mac.sh"])


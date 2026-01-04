import subprocess
import os
import sys

if os.geteuid() != 0:
    print("This script must be run as root. Please use sudo.")
    sys.exit(1)
def arp_scan_save_macs(output_file="mac.txt", timeout=30):
    try:
        result = subprocess.run(
            ["sudo", "arp-scan", "--localnet", "--plain"],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=True
        )
    except subprocess.TimeoutExpired:
        print("ARP scan timed out")
        return
    except subprocess.CalledProcessError as e:
        print("arp-scan fail")
        return

    mac_addresses = set()

    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) >= 2:
            mac_addresses.add(parts[1])

    # List MAC addresses
    print("MAC addresses found:")
    for mac in sorted(mac_addresses):
        print(mac)

    # Save to mac.txt
    with open(output_file, "w") as f:
        for mac in sorted(mac_addresses):
            f.write(mac + "\n")

    print(f"\nSaved {len(mac_addresses)} MAC addresses to {output_file}")


if __name__ == "__main__":
    arp_scan_save_macs()

#run mac.sh

subprocess.run(["bash", "mac.sh"])



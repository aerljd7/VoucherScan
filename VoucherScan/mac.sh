
#ifconfig <interface> hw ether <new_mac_address>

#!/bin/bash

MAC_FILE="mac.txt"

# Must be run as root
if [[ $EUID -ne 0 ]]; then
  echo "Please run as root (sudo)."
  exit 1
fi

# Check mac.txt exists
if [[ ! -f "$MAC_FILE" ]]; then
  echo "File $MAC_FILE not found."
  exit 1
fi

# Ask for interface
read -rp "Enter network interface (e.g. eth0, wlo1, wlan0): " IFACE

# Check interface exists
if ! ip link show "$IFACE" &>/dev/null; then
  echo "Interface $IFACE does not exist."
  exit 1
fi

echo
echo "Available MAC addresses:"
echo "-------------------------"

# Load MACs into array
mapfile -t MACS < "$MAC_FILE"

if [[ ${#MACS[@]} -eq 0 ]]; then
  echo "No MAC addresses found in $MAC_FILE."
  exit 1
fi

# Display numbered list
for i in "${!MACS[@]}"; do
  printf "[%d] %s\n" $((i+1)) "${MACS[$i]}"
done

echo
read -rp "Select MAC number: " SELECTION

# Validate selection
if ! [[ "$SELECTION" =~ ^[0-9]+$ ]] || (( SELECTION < 1 || SELECTION > ${#MACS[@]} )); then
  echo "Invalid selection."
  exit 1
fi

NEW_MAC="${MACS[$((SELECTION-1))]}"

# Validate MAC format
if ! [[ "$NEW_MAC" =~ ^([a-fA-F0-9]{2}:){5}[a-fA-F0-9]{2}$ ]]; then
  echo "Invalid MAC address format: $NEW_MAC"
  exit 1
fi

echo
echo "Changing MAC address of $IFACE to $NEW_MAC"

# Apply MAC address
ip link set "$IFACE" down
ifconfig "$IFACE" hw ether "$NEW_MAC"
ip link set "$IFACE" up

echo "MAC address successfully changed."


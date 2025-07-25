#!/bin/bash

#Example Script that Runs Common Fixes on macOS

# Run Disk Utility First Aid on startup disk
echo "Running Disk Utility First Aid on startup disk..."
diskutil verifyVolume /
if [ $? -ne 0 ]; then
    echo "Errors found on startup disk. Attempting to repair..."
    diskutil repairVolume /
    if [ $? -eq 0 ]; then
        echo "Disk repair completed successfully."
    else
        echo "Disk repair failed. Manual intervention might be required."
    fi
else
    echo "No issues found on startup disk."
fi

# Clear system caches
echo "Clearing system caches..."
sudo rm -rf /Library/Caches/*
sudo rm -rf ~/Library/Caches/*
echo "System caches cleared."

# Reset DNS
sudo dscacheutil -flushcache                # Flush DNS cache
sudo killall -HUP mDNSResponder             # Restart mDNSResponder
echo "DNS Flushed."

# Clear out old temporary files
echo "Clearing temporary files..."
sudo rm -rf /tmp/*
echo "Temporary files cleared."

# Check for system updates
echo "Checking for macOS software updates..."
softwareupdate -l
echo "Please install any available updates manually if listed above."

# Optionally, you might want to run a permissions repair, but since macOS High Sierra, this has become less relevant:
# echo "Repairing disk permissions..."
diskutil repairPermissions /

echo "Common fixes script completed. Some actions might require manual restart or intervention."
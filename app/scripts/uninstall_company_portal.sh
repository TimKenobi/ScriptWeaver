#!/bin/bash

# Script to uninstall Microsoft Company Portal on macOS
# Created: July 25, 2025
# Requires: sudo privileges for file deletion and keychain access
# Logs: /var/log/company_portal_uninstall.log

# Set up logging
LOG_FILE="/var/log/company_portal_uninstall.log"
if [[ ! -d "/var/log" ]]; then
    mkdir -p "/var/log"
fi
exec > >(tee -a "$LOG_FILE") 2>&1
echo "$(date) | Starting uninstallation of Microsoft Company Portal"

# Function to check if a process is running and terminate it
terminate_process() {
    local process_name="$1"
    if pgrep -f "$process_name" > /dev/null; then
        echo "$(date) | Terminating process: $process_name"
        pkill -f "$process_name" || {
            echo "$(date) | Failed to terminate $process_name"
            exit 1
        }
    else
        echo "$(date) | No $process_name process found"
    fi
}

# Function to remove a file or directory if it exists
remove_item() {
    local item_path="$1"
    if [[ -e "$item_path" ]]; then
        echo "$(date) | Removing $item_path"
        sudo rm -rf "$item_path" || {
            echo "$(date) | Failed to remove $item_path"
            exit 1
        }
    else
        echo "$(date) | $item_path not found, skipping"
    fi
}

# Function to remove keychain entries related to Microsoft, Intune, or Company Portal
remove_keychain_entries() {
    echo "$(date) | Removing keychain entries for Microsoft, Intune, and Company Portal"
    local logged_in_user=$(stat -f "%Su" /dev/console)
    
    # Search for and delete keychain items matching Microsoft, Intune, or Company Portal
    sudo -u "$logged_in_user" security find-certificate -a -Z | grep -E "Microsoft|Intune|Company Portal|DeviceLogin.microsoft.com" | while read -r line; do
        if [[ $line =~ "SHA-1 hash: " ]]; then
            local cert_hash=$(echo "$line" | awk '{print $3}')
            echo "$(date) | Removing keychain certificate with hash: $cert_hash"
            sudo -u "$logged_in_user" security delete-certificate -Z "$cert_hash" || {
                echo "$(date) | Failed to remove certificate with hash: $cert_hash"
            }
        fi
    done
    
    # Remove specific MS-ORGANIZATION-ACCESS certificate
    local aad_id=$(sudo -u "$logged_in_user" security find-certificate -a -Z | grep -B 9 "MS-ORGANIZATION-ACCESS" | awk '/"alis"<blob>=/ {print $NF}' | sed 's/"alis"<blob>="//;s/.$//')
    if [[ -n "$aad_id" ]]; then
        echo "$(date) | Removing MS-ORGANIZATION-ACCESS certificate"
        sudo -u "$logged_in_user" security delete-certificate -c "MS-ORGANIZATION-ACCESS" || {
            echo "$(date) | Failed to remove MS-ORGANIZATION-ACCESS certificate"
        }
    else
        echo "$(date) | No MS-ORGANIZATION-ACCESS certificate found"
    fi
    
    # Remove primaryrefresh entries
    sudo -u "$logged_in_user" security find-generic-password -s "primaryrefresh" | while read -r line; do
        echo "$(date) | Removing primaryrefresh keychain entry"
        sudo -u "$logged_in_user" security delete-generic-password -s "primaryrefresh" || {
            echo "$(date) | Failed to remove primaryrefresh entry"
        }
    done
}

# Step 1: Terminate Company Portal and related processes
echo "$(date) | Terminating Company Portal and JAMF processes"
terminate_process "Company Portal"
terminate_process "JAMF"

# Step 2: Remove Company Portal application
remove_item "/Applications/Company Portal.app"

# Step 3: Remove associated files and preferences
echo "$(date) | Removing associated files and preferences"
remove_item "/Library/Application Support/com.microsoft.CompanyPortal.usercontext.info"
remove_item "/Library/Application Support/com.microsoft.CompanyPortal"
remove_item "/Library/Application Support/com.jamfsoftware.selfservice.mac"
remove_item "/Library/Saved Application State/com.microsoft.CompanyPortal.savedState"
remove_item "/Library/Saved Application State/com.jamfsoftware.selfservice.mac.savedState"
remove_item "/Library/Preferences/com.microsoft.CompanyPortal.plist"
remove_item "/Library/Preferences/com.jamfsoftware.selfservice.mac.plist"
remove_item "/Library/Preferences/com.jamfsoftware.management.jamfAAD.plist"

# Step 4: Remove user-specific files
logged_in_user=$(stat -f "%Su" /dev/console)
if [[ -n "$logged_in_user" ]]; then
    remove_item "/Users/$logged_in_user/Library/Cookies/com.microsoft.CompanyPortal.binarycookies"
    remove_item "/Users/$logged_in_user/Library/Cookies/com.jamfsoftware.management.jamfAAD.binarycookies"
else
    echo "$(date) | No logged-in user found, skipping user-specific file removal"
fi

# Step 5: Remove keychain entries
remove_keychain_entries

# Step 6: Remove MDM configuration profile (if applicable)
# Note: Uncomment the following lines if you need to remove Jamf MDM profiles
# echo "$(date) | Removing Jamf MDM profile (uncomment to enable)"
# sudo jamf removemdmprofile || echo "$(date) | Failed to remove MDM profile"
# sudo jamf removeFramework || echo "$(date) | Failed to remove Jamf framework"

# Step 7: Verify removal
if [[ ! -d "/Applications/Company Portal.app" ]]; then
    echo "$(date) | Company Portal successfully uninstalled"
else
    echo "$(date) | Error: Company Portal app still exists"
    exit 1
fi

# Step 8: Optional - Remove the device from Intune (manual step reminder)
echo "$(date) | Note: To fully unenroll the device from Intune, open Company Portal (if reinstalled) or remove the management profile via System Settings > Profiles. See: https://learn.microsoft.com/en-us/mem/intune/user-help/unenroll-your-device-from-intune-macos"

echo "$(date) | Uninstallation complete. Log saved to $LOG_FILE"
exit 0
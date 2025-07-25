#!/bin/bash

#Example of a script to install a configuration profile for management of Macs on your network
#This script disables a user's ability to connect their personal OneDrive account with a business account

# Check if the script is run with root privileges
if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 
   exit 1
fi

# Here document to include the profile content
cat << EOF > /tmp/disableonedrive.mobileconfig
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>PayloadContent</key>
    <array>
        <dict>
            <key>PayloadDisplayName</key>
            <string>OneDrive Restrictions</string>
            <key>PayloadIdentifier</key>
            <string>com.yourcompany.onedrive.restrictions</string>
            <key>PayloadOrganization</key>
            <string>YourCompany</string>
            <key>PayloadType</key>
            <string>com.microsoft.OneDrive</string>
            <key>PayloadUUID</key>
            <string>00000000-0000-0000-0000-000000000000</string>
            <key>PayloadVersion</key>
            <integer>1</integer>
            <key>DisablePersonalSync</key>
            <true/>
        </dict>
    </array>
    <key>PayloadDisplayName</key>
    <string>OneDrive Personal Sync Restriction</string>
    <key>PayloadIdentifier</key>
    <string>com.yourcompany.main</string>
    <key>PayloadOrganization</key>
    <string>YourCompany</string>
    <key>PayloadScope</key>
    <string>System</string>
    <key>PayloadType</key>
    <string>Configuration</string>
    <key>PayloadUUID</key>
    <string>00000000-0000-0000-0000-000000000000</string>
    <key>PayloadVersion</key>
    <integer>1</integer>
</dict>
</plist>
EOF

# Install the profile
/usr/bin/profiles -I -F /tmp/disableonedrive.mobileconfig

# Check the exit status of the profiles command
if [ $? -eq 0 ]; then
    echo "Profile installed successfully."
    # Clean up the temporary profile file
    rm /tmp/disableonedrive.mobileconfig
else
    echo "Failed to install profile."
fi
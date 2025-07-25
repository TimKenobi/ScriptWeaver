#!/bin/bash

# Define the download URL for Office 365 for Mac
URL="https://go.microsoft.com/fwlink/?linkid=525133"

# Define the path where the Office installer will be downloaded
DOWNLOAD_PATH="/tmp/Microsoft_Office_365_Installer.pkg"

# Ensure /tmp directory exists
if [ ! -d "/tmp" ]; then
    echo "/tmp directory not found, creating it..."
    sudo mkdir -p /tmp
    sudo chmod 1777 /tmp  # Set permissions to be world-writable with sticky bit
fi

# Download Office 365 installer
echo "Downloading Office 365 for Mac..."
curl -L -o "$DOWNLOAD_PATH" "$URL"

# Check if the download was successful
if [ $? -eq 0 ]; then
    echo "Download completed successfully."

    # Install Office 365
    echo "Installing Office 365 for Mac..."
    sudo installer -pkg "$DOWNLOAD_PATH" -target /
    
    # Check if installation was successful
    if [ $? -eq 0 ]; then
        echo "Office 365 has been installed successfully. Please sign in to activate."
    else
        echo "Installation failed. Please check the logs for details."
    fi
else
    echo "Download failed. Check your internet connection or URL."
fi

# Clean up the downloaded installer file
echo "Cleaning up..."
rm -f "$DOWNLOAD_PATH"

echo "Script execution completed."
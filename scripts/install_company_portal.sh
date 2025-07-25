#!/bin/bash

# Define the updated download URL for the Company Portal installer
URL="https://go.microsoft.com/fwlink/?linkid=853070"

# Define the path where the installer will be downloaded
DOWNLOAD_PATH="/tmp/CompanyPortal.pkg"

# Ensure /tmp directory exists
if [ ! -d "/tmp" ]; then
    echo "/tmp directory not found, creating it..."
    sudo mkdir -p /tmp
    sudo chmod 1777 /tmp  # Set permissions to be world-writable with sticky bit
fi

# Download the Company Portal installer
echo "Downloading Company Portal..."
curl -L -o "$DOWNLOAD_PATH" "$URL"

# Check if the download was successful
if [ $? -eq 0 ]; then
    echo "Download completed successfully."
    
    # Install the Company Portal
    echo "Installing Company Portal..."
    sudo installer -pkg "$DOWNLOAD_PATH" -target /
    
    # Check if installation was successful
    if [ $? -eq 0 ]; then
        echo "Company Portal has been installed successfully."
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

open -a "Company Portal"
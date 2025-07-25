#!/bin/bash

# Function to check if Windows App is installed
is_remote_desktop_installed() {
    if [ -d "/Applications/Windows App.app" ]; then
        return 0
    else
        return 1
    fi
}

# Install Windows App if not installed
if ! is_remote_desktop_installed; then
    echo "Windows App is not installed. Downloading and installing..."
    curl -L "https://go.microsoft.com/fwlink/?linkid=868963" -o ~/Downloads/WindowsApp.pkg
    sudo installer -pkg ~/Downloads/WindowsApp.pkg -target /
    rm ~/Downloads/WindowsApp.pkg
    echo "Windows App has been installed."
else
    echo "Windows App is already installed."
fi

# Check for updates (Microsoft Teams auto-updates)
echo "Windows App checks for updates automatically. However, we'll restart it to ensure it checks."
if pgrep -f "Windows App" > /dev/null; then
    osascript -e 'tell application "Windows App" to quit'
fi
open -a "Windows App"
echo "Windows App has been opened to check for updates. Please check manually if an update was applied or not."
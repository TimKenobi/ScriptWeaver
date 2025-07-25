#!/bin/bash

# Function to check if an application is installed
is_app_installed() {
    if [ -d "/Applications/$1.app" ]; then
        return 0
    else
        return 1
    fi
}

# Install Microsoft Edge if not installed
if ! is_app_installed "Microsoft Edge"; then
    echo "Microsoft Edge is not installed. Downloading and installing..."
    curl -L "https://go.microsoft.com/fwlink/?linkid=2093504" -o ~/Downloads/MicrosoftEdge.pkg
    sudo installer -pkg ~/Downloads/MicrosoftEdge.pkg -target /
    rm ~/Downloads/MicrosoftEdge.pkg
    echo "Microsoft Edge has been installed."
else
    echo "Microsoft Edge is already installed."
fi

# Install Google Chrome if not installed
if ! is_app_installed "Google Chrome"; then
    echo "Google Chrome is not installed. Downloading and installing..."
    curl -L "https://dl.google.com/chrome/mac/stable/accept_tos%3Dhttps%253A%252F%252Fwww.google.com%252Fintl%252Fen_ph%252Fchrome%252Fterms%252F%26_and_accept_tos%3Dhttps%253A%252F%252Fpolicies.google.com%252Fterms/googlechrome.pkg" -o ~/Downloads/GoogleChrome.pkg
    sudo installer -pkg ~/Downloads/GoogleChrome.pkg -target /
    rm ~/Downloads/GoogleChrome.pkg
    echo "Google Chrome has been installed."
else
    echo "Google Chrome is already installed."
fi

# Install Zoom if not installed
if ! is_app_installed "zoom.us"; then
    echo "Zoom is not installed. Downloading and installing..."
    curl -L "https://zoom.us/client/latest/ZoomInstallerIT.pkg" -o ~/Downloads/ZoomInstallerIT.pkg
    sudo installer -pkg ~/Downloads/ZoomInstallerIT.pkg -target /
    rm ~/Downloads/ZoomInstallerIT.pkg
    echo "Zoom has been installed."
else
    echo "Zoom is already installed."
fi
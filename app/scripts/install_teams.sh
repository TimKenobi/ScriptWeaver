#!/bin/bash

# Function to check if Microsoft Teams is installed
is_teams_installed() {
    if [ -d "/Applications/Microsoft Teams.app" ]; then
        return 0
    else
        return 1
    fi
}

# Install Microsoft Teams if not installed
if ! is_teams_installed; then
    echo "Microsoft Teams is not installed. Downloading and installing..."
    curl -L "https://go.microsoft.com/fwlink/?linkid=869428" -o ~/Downloads/MicrosoftTeams.pkg
    sudo installer -pkg ~/Downloads/MicrosoftTeams.pkg -target /
    rm ~/Downloads/MicrosoftTeams.pkg
    echo "Microsoft Teams has been installed."
else
    echo "Microsoft Teams is already installed."
fi

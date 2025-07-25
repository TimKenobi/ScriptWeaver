#!/bin/bash

# Function to check if Firefox is installed
is_firefox_installed() {
    if [ -d "/Applications/Firefox.app" ]; then
        return 0
    else
        return 1
    fi
}

# Install Firefox if not installed
if ! is_firefox_installed; then
    echo "Firefox is not installed. Downloading and installing..."
    curl -L "https://download.mozilla.org/?product=firefox-latest&os=osx&lang=en-US" -o ~/Downloads/Firefox.dmg
    hdiutil attach ~/Downloads/Firefox.dmg
    sudo cp -R /Volumes/Firefox/Firefox.app /Applications/
    hdiutil detach /Volumes/Firefox
    rm ~/Downloads/Firefox.dmg
    echo "Firefox has been installed."
else
    echo "Firefox is already installed."
fi

# Check for updates
echo "Checking for Firefox updates..."
/Applications/Firefox.app/Contents/MacOS/firefox-bin -silent -P default &>/dev/null & disown
sleep 10  # Give Firefox some time to start and check for updates
osascript -e 'tell application "Firefox" to quit'

# Note: Automatic update check is built into Firefox, but this script manually triggers it.
echo "Firefox update check has been initiated. Please check manually if an update was applied or not."
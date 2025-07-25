#!/bin/bash

set -e

# List of applications (labels) and their typical installation paths
# Format: "InstallomatorLabel|/Path/To/App"
APPS=(
  "microsoftedge|/Applications/Microsoft Edge.app"
  "googlechrome|/Applications/Google Chrome.app"
  "firefox|/Applications/Firefox.app"
  "zoom|/Applications/zoom.us.app"
  "microsoftteams|/Applications/Microsoft Teams.app"
)

INSTALLOMATOR_URL="https://raw.githubusercontent.com/Installomator/Installomator/main/Installomator.sh"
INSTALLOMATOR_LOCAL="Installomator.sh"

# Download Installomator if not already present
if [[ ! -f "$INSTALLOMATOR_LOCAL" ]]; then
  echo "Downloading Installomator..."
  curl -fsSL "$INSTALLOMATOR_URL" -o "$INSTALLOMATOR_LOCAL"
  chmod +x "$INSTALLOMATOR_LOCAL"
fi

# Loop through each app in our list
for APP_INFO in "${APPS[@]}"; do
  LABEL="${APP_INFO%%|*}"
  APP_PATH="${APP_INFO#*|}"

  echo "Checking: $LABEL"
  if [[ -d "$APP_PATH" ]]; then
    echo "  - Found at: $APP_PATH"
    echo "  - Updating $LABEL..."
  else
    echo "  - Not installed, installing $LABEL..."
  fi

  sudo ./"$INSTALLOMATOR_LOCAL" "$LABEL" LOGO=0
  echo
done

echo "All specified apps have been checked and installed/updated as needed."

# Handle macOS system updates
echo "Checking for macOS software updates..."
sudo softwareupdate -i -a  # Install all available macOS software updates

# Check for macOS OS upgrades
echo "Checking for macOS OS upgrades (this might require manual interaction)..."
sudo softwareupdate -l

echo "Please note: macOS upgrades might require manual intervention. Check the output above for any recommendations."


echo "Script execution completed."
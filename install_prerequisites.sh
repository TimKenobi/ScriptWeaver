# ~/ScriptManager/app/scripts/prerequisites.sh
#!/bin/bash

echo "Installing prerequisites..."

# Install Homebrew if not installed
if ! command -v brew &> /dev/null; then
    echo "Homebrew not found. Installing..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Install required packages
brew install python3 git wget curl jq

# Install Python dependencies
pip3 install -r ~/ScriptManager/requirements.txt

echo "Prerequisites installed successfully!"
#!/bin/bash

# Define the output file
output_file="/tmp/installed_software.txt"

{
  echo "=========================="
  echo "Application Versions in /Applications:"
  echo "--------------------------"
  for app in /Applications/*.app; do
      if [ -d "$app" ]; then
         appName=$(basename "$app")
         # Attempt to read the CFBundleShortVersionString; if not found, indicate as such.
         version=$(defaults read "$app/Contents/Info.plist" CFBundleShortVersionString 2>/dev/null)
         if [ -z "$version" ]; then
            version="Version not found"
         fi
         echo "$appName: $version"
      fi
  done
  echo ""

  echo "=========================="
  echo "macOS Version Information:"
  echo "--------------------------"
  sw_vers
  echo ""
  
} > "$output_file" 2>&1

# Open the output file in TextEdit
open -e "$output_file"
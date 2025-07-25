#!/bin/bash

output_file="/tmp/network_output.txt"

{
    echo "Checking network..."
    ping -c 4 google.com
    echo "Running traceroute..."
    traceroute google.com
    echo "DNS Check:"
    dig google.com
} > "$output_file" 2>&1

# Open the output file in the default text editor (TextEdit on macOS)
open -e "$output_file"
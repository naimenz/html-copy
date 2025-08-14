#!/bin/bash

echo "=== Clipboard Analysis ==="

# Get clipboard info
echo "Available formats:"
osascript -e "
set clipInfo to clipboard info
repeat with formatInfo in clipInfo
    log \"  \" & (item 1 of formatInfo) & \" (\" & (item 2 of formatInfo) & \" bytes)\"
end repeat"

echo -e "\n=== Plain Text Content ==="
osascript -e "get the clipboard as string"

echo -e "\n=== HTML Content ==="
# Get the raw HTML data and extract/decode the hex
html_raw=$(osascript -e "get the clipboard as «class HTML»")
if [[ $html_raw == *"«data HTML"* ]]; then
    # Extract hex data (everything between HTML and final »)
    hex_data=$(echo "$html_raw" | sed 's/.*«data HTML\(.*\)».*/\1/')
    # Decode hex to readable text
    echo "$hex_data" | xxd -r -p
else
    echo "$html_raw"
fi

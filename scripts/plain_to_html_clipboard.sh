#!/bin/bash
# plain_to_html_clipboard.sh

current_text=$(pbpaste)
if [[ -z "$current_text" ]]; then
    echo "No text in clipboard"
    exit 1
fi

# Convert text to hex
hex_data=$(echo -n "$current_text" | xxd -p | tr -d '\n')

# Set clipboard with raw hex data
osascript -e "set the clipboard to «data HTML${hex_data}»"

if [[ $? -eq 0 ]]; then
    echo "✓ Set clipboard HTML format to current plain text"
    echo "Content: $current_text"
else
    echo "✗ Failed to set HTML clipboard format"
fi

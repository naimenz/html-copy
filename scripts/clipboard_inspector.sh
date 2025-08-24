#!/bin/bash
# inspect_clipboard.sh

PRETTY=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --pretty|-p)
            PRETTY=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [--pretty]"
            echo "  --pretty  : Format HTML output (requires prettier: npm install -g prettier)"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

prettify_html() {
    if command -v prettier >/dev/null 2>&1; then
        echo "$1" | prettier --parser html --tab-width 2
    elif command -v html-beautify >/dev/null 2>&1; then
        echo "$1" | html-beautify --indent-size 2
    else
        echo "No HTML formatter found. Install prettier: npm install -g prettier"
        echo "$1"
    fi
}

echo "=== Clipboard Inspector ==="

# Show available formats
echo "Available formats:"
osascript -e "
set clipInfo to clipboard info
repeat with formatInfo in clipInfo
    log \"  \" & (item 1 of formatInfo) & \" (\" & (item 2 of formatInfo) & \" bytes)\"
end repeat"

# Plain text
echo -e "\n--- Plain Text ---"
pbpaste

# HTML content
echo -e "\n--- HTML Content ---"
html_raw=$(osascript -e "get the clipboard as «class HTML»" 2>/dev/null)

if [[ -n "$html_raw" && $html_raw == *"«data HTML"* ]]; then
    hex_data=$(echo "$html_raw" | sed 's/.*«data HTML\(.*\)».*/\1/')
    decoded_html=$(echo "$hex_data" | xxd -r -p 2>/dev/null)

    if [[ -n "$decoded_html" ]]; then
        if [[ "$PRETTY" == true ]]; then
            prettify_html "$decoded_html"
        else
            echo "$decoded_html"
        fi
    else
        echo "Failed to decode HTML"
    fi
else
    echo "No HTML content available"
fi

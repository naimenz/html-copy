import pyperclip
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QClipboard
from PyQt5 import QtCore

# Create a Qt application instance
app = QApplication([])


# Function to copy text to the clipboard
def copy_to_clipboard(text):
    clipboard = app.clipboard()
    clipboard.setText(text)


# Function to paste text from the clipboard
def paste_from_clipboard():
    clipboard = app.clipboard()
    return clipboard.text()


def copy_html_to_clipboard(html):
    clipboard = app.clipboard()
    mime_data = QtCore.QMimeData()
    mime_data.setHtml("This is <b>HTML</b>")
    mime_data.setText("This is text")
    clipboard.setMimeData(mime_data)


def paste_html_from_clipboard():
    clipboard = app.clipboard()
    mime_data = clipboard.mimeData()
    if mime_data.hasHtml():
        return mime_data.html()
    else:
        return None


# Example usage

copy_to_clipboard("Hello, Qt Clipboard!")
copy_html_to_clipboard(
    """<meta charset='utf-8'><ul data-stringify-type="unordered-list" class="p-rich_text_list p-rich_text_list__bullet" data-indent="0" data-border="0" style="box-sizing: inherit; margin: 0px; padding: 0px; list-style-type: none; color: rgb(209, 210, 211); font-family: Slack-Lato, Slack-Fractions, appleLogo, sans-serif; font-size: 15px; font-style: normal; font-variant-ligatures: common-ligatures; font-variant-caps: normal; font-weight: 400; letter-spacing: normal; orphans: 2; text-align: left; text-indent: 0px; text-transform: none; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; white-space: normal; background-color: rgb(34, 37, 41); text-decoration-thickness: initial; text-decoration-style: initial; text-decoration-color: initial;"><li data-stringify-indent="0" data-stringify-border="0" style="box-sizing: inherit; margin-bottom: 0px; margin-left: var(--dt_static_space-175); list-style-type: none;">Pay for a mobile barista service, a mobile massage service, or similar fun destressing services to come to Constellation</li><li data-stringify-indent="0" data-stringify-border="0" style="box-sizing: inherit; margin-bottom: 0px; margin-left: var(--dt_static_space-175); list-style-type: none;">For barista, it's just open bar for a few hours</li></ul>"""
)
print(paste_html_from_clipboard())

while True:
    text = pyperclip.waitForNewPaste()
    print(f"New text on clipboard from pyperclip: {text}")
    print(f"New text/plain from Qt: {paste_from_clipboard()}")
    print(f"New text/html from Qt: {paste_html_from_clipboard()}")
    print("Setting clipboard to 'Hello, Qt Clipboard!'")
    copy_to_clipboard("Hello, Qt Clipboard!")

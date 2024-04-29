from dataclasses import dataclass
import time
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QClipboard
from PyQt5 import QtCore
from PyQt5.QtCore import QMimeData
import sys

from slack_copy.abstract_markdown import AbstractMarkdownTree

@dataclass
class ClipboardContents:
    text: str
    html: str

SourceIndicators = {
    "gdocs": "docs-internal",
    "obsidian": "Microsoft YaHei Light",
    "slack": "Slack",
}

class ClipboardWrapper:
    def __init__(self):
        # Ensure a QApplication instance exists
        self.app = QApplication.instance() or QApplication(sys.argv)
        self.clipboard: QClipboard = self.app.clipboard()  # type: ignore
        self.loop = None

    def get_clipboard_contents(self):
        text = self.clipboard.text()
        mime_data: QMimeData = self.clipboard.mimeData()  # type: ignore
        if mime_data.hasHtml():
            html = mime_data.html()
        else:
            html = ""
        return ClipboardContents(text, html)
    
    def set_clipboard_contents(self, contents: ClipboardContents):
        mime_data = QtCore.QMimeData()
        mime_data.setText(contents.text)
        mime_data.setHtml(contents.html)
        self.clipboard.setMimeData(mime_data)

    def wait_for_new_paste(self, sleep_seconds: float = 0.1) -> ClipboardContents:
        """Waits for new content on the clipboard."""
        original_contents = self.get_clipboard_contents()
        while True:
            current_contents = self.get_clipboard_contents()
            if current_contents != original_contents:
                return current_contents
            time.sleep(sleep_seconds)

    def shutdown(self):
        self.app.quit()

def html_to_amtree(html: str) -> AbstractMarkdownTree:
    # work out which kind of html it is and then parse
    if SourceIndicators["gdocs"] in html:
        return AbstractMarkdownTree.from_gdocs(html)
    elif SourceIndicators["slack"] in html:
        return AbstractMarkdownTree.from_slack(html)
    # I think this font is only used in Obsidian
    elif SourceIndicators["obsidian"] in html:
        raise NotImplementedError("Haven't implemented parsing from Obsidian yet")
    else:
        raise ValueError("Unknown source for HTML")

def text_to_amtree(text: str) -> AbstractMarkdownTree:
    # for now, we'll assume that if it's not HTML, it's from Obsidian
    return AbstractMarkdownTree.from_obsidian(text, is_html=False)

def cb_to_amtree(contents: ClipboardContents) -> AbstractMarkdownTree:
    if contents.html != "":
        amtree = html_to_amtree(contents.html)
    else:
        amtree = text_to_amtree(contents.text)
    return amtree

def process_contents(contents: ClipboardContents) -> ClipboardContents:
    try:
        amtree = cb_to_amtree(contents)
    except ValueError as e:
        print(f"Couldn't parse: {contents}")
        print(f"Error: {e}")
        return contents
    html = amtree.to_html()
    return ClipboardContents(contents.text, html)
 
def main():
    while True:
        cb = ClipboardWrapper()
        contents = cb.wait_for_new_paste() 
        processed_contents = process_contents(contents) 
        cb.set_clipboard_contents(processed_contents)
        contents = cb.get_clipboard_contents()
        cb.shutdown()
        # we have to delete and recreate to avoid a hanging bug
        # TODO (gh#1): fix the hanging bug
        del cb

if __name__ == "__main__":
    main()
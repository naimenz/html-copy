import time
import pyperclip
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QEventLoop
from PyQt5.QtGui import QClipboard
from PyQt5 import QtCore
import sys

def main():
    app = QApplication([])
    while True:
        _ = pyperclip.waitForNewPaste()
        clipboard = app.clipboard()
        text = clipboard.text()
        # modify text
        text = text + " [modified]"
        clipboard.setText(text)

if __name__ == "__main__":
    main()
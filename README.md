# Slack Copy
The purpose of this repo is to make it easier to copy and paste markdown and rich text from one app into another. The current goal is to support copying between any of:
- Google Docs
- Slack
- Obsidian

Currently I'm focusing on Slack -> Google Docs.

## Usage
Current usage is a little awkward; I plan to improve this.

To use it at the moment, you should:
1. Install it like any Python project, for example:
    1. Clone the repo
    2. Make a new `venv`
    3. Run `pip install .`
2. From inside, that `venv`, run `slack-copy`
    - This will start a loop that checks your clipboard and modifies it if it finds a match to one of the formats it can parse.
        - Your clipboard is processed locally using `PyQt5`
        - You clipboard content is not stored or sent anywhere.
        - If the format is not a match, it should leave your clipboard alone.
3. I'd recommend opening a new terminal, activating the `venv`, running `slack-copy` in there, and leaving it open. 

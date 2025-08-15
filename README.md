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
    2. Make a new `venv`:
        1. Run `python -m venv .venv`
        2. Activate the `venv` with `source .venv/bin/activate`
        3. Run `pip install .`
    3. Alternatively if you have `uv` installed you can do:
        1. `uv venv`
        2. `uv sync`
2. You may encounter some errors installing - if so, use `brew`/`apt` to install the  missing dependencies.
3. From inside, that `venv`, run `slack-copy`
    - This will start a loop that checks your clipboard and modifies it if it finds a match to one of the formats it can parse.
        - Your clipboard is processed locally using `PyQt5`
        - You clipboard content is not stored or sent anywhere.
        - If the format is not a match, it should leave your clipboard alone.
4. I'd recommend opening a new terminal, activating the `venv`, running `slack-copy` in there, and leaving it open. 

## Currently Supported Workflows
This is very much an alpha, so 'supported' means 'it works at all, on some minimal examples'. Let me know if there are specific bugs or missing features that are impacting your ability to use the app.

### Slack
- Copying from Slack is reasonably well-supported.
- Copying to Slack is reasonably well-supported, by converting to Markdown.
### Google docs
- Copying from GDocs is reasonably well-supported.
- Copying to GDocs is reasonably well-supported, either as HTML or as 'right click -> paste from Markdown'
### Obsidian
- Copying from Obsidian is reasonably well-supported as Markdown (in `edit` mode), and less good as rich text (in `view` mode)
- Copying to Obsidian is reasonably well-supported.
### Airtable
- Copying from Airtable has been used in practice and works okay.
- Copying to Airtable is untested.
### Other apps
- Let me know if there are other apps you'd like to have supported.
- I might try Google Chat soon.
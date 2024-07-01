import re
import markdown

from slack_copy.html_parsers.airtable_parser import AirtableParser
from slack_copy.html_parsers.html_parser import HTMLParser
from slack_copy.html_parsers.slack_parser import SlackParser
from slack_copy.nodes import AMNode


class AbstractMarkdownTree:
    """
    Abstract representation of markdown content.

    Represents a markdown file in a way that is independent of the actual implementation.
    This way we can convert to and from different formats (e.g. Slack, Obsidian, etc.)
    """

    def __init__(self, root: AMNode) -> None:
        self.root = root

    def to_html(self) -> str:
        return self.root.to_html()

    @staticmethod
    def from_obsidian(text: str, is_html: bool = True) -> "AbstractMarkdownTree":
        if not is_html:
            text = parse_obsidian_markdown(text)
        parser = HTMLParser()
        root = parser.parse(text)
        assert root is not None
        return AbstractMarkdownTree(root)

    def to_obsidian(self) -> str:
        raise NotImplementedError

    @staticmethod
    def from_slack(text: str) -> "AbstractMarkdownTree":
        parser = SlackParser()
        root = parser.parse(text)
        assert root is not None
        return AbstractMarkdownTree(root)

    @staticmethod
    def from_airtable(text: str) -> "AbstractMarkdownTree":
        parser = AirtableParser()
        root = parser.parse(text)
        assert root is not None
        return AbstractMarkdownTree(root)

    def to_slack(self) -> str:
        raise NotImplementedError

    @staticmethod
    def from_gdocs(text: str) -> "AbstractMarkdownTree":
        parser = HTMLParser()
        root = parser.parse(text)
        assert root is not None
        return AbstractMarkdownTree(root)

    def to_gdocs(self) -> str:
        raise NotImplementedError


def parse_obsidian_markdown(text):
    """Parse obsidian-flavored markdown (in particular, lists) into HTML.

    (Help from https://claude.ai/chat/63a0feed-2065-4216-90d5-b10232326d5b)"""
    preprocessed_text = preprocess_obsidian_markdown(text)
    html = markdown.markdown(preprocessed_text, extensions=["sane_lists"])
    return html


def preprocess_obsidian_markdown(text):
    # Regular expression pattern to match text followed by a list without a newline
    pattern = re.compile(r"(.*)\n((?:[*+-] .*(?:\n|$))+)", re.MULTILINE)

    # Replace matched patterns with text followed by two newlines and the list
    def replace_unordered(match):
        return f"{match.group(1)}\n\n{match.group(2)}"

    processed_text = pattern.sub(replace_unordered, text)

    pattern = re.compile(r"(.*)\n((?:\d+\. .*(?:\n|$))+)", re.MULTILINE)

    # Replace matched patterns with text followed by two newlines and the list
    def replace_ordered(match):
        return f"{match.group(1)}\n\n{match.group(2)}"

    processed_text = pattern.sub(replace_ordered, processed_text)

    # Add a newline between the end of the list and continued text
    # (from https://claude.ai/chat/78f86edb-cd82-43b4-bae2-ea891f9a1f67)
    pattern = r"(?m)^(?:(?:\s*\d+\.|\s*-)\s+.*(?:\n(?:\s*\d+\.|\s*-)\s+.*)*)\n(?!\s*(?:\d+\.|-)\s)"
    processed_text = re.sub(pattern, r"\g<0>\n", processed_text)

    return processed_text

import re
import typing
import markdown
from typing import Literal

import bs4

from slack_copy.nodes import AMLeaf, AMList, AMNode, AMContainer

Style = Literal["bold", "italic", "underline", "strikethrough", "code"]
styles: tuple[Style, ...] = typing.get_args(Style)


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
        soup = bs4.BeautifulSoup(text, "lxml")
        root = _parse_soup_tag(soup)
        assert root is not None
        return AbstractMarkdownTree(root)

    def to_obsidian(self) -> str:
        raise NotImplementedError

    @staticmethod
    def from_slack(text: str) -> "AbstractMarkdownTree":
        soup = bs4.BeautifulSoup(text, "lxml")
        root = _parse_soup_tag(soup)
        assert root is not None
        return AbstractMarkdownTree(root)

    def to_slack(self) -> str:
        raise NotImplementedError

    @staticmethod
    def from_gdocs(text: str) -> "AbstractMarkdownTree":
        soup = bs4.BeautifulSoup(text, "lxml")
        root = _parse_soup_tag(soup)
        assert root is not None
        return AbstractMarkdownTree(root)

    def to_gdocs(self) -> str:
        raise NotImplementedError


def _parse_soup_tag(tag: bs4.element.PageElement) -> AMNode | None:
    """
    Parse HTML and return an AbstractMarkdownTree.
    """
    # base cases
    if isinstance(tag, bs4.element.NavigableString):
        if tag.strip() == "":
            # skipping solitary newlines and empty strings
            return None
        return AMLeaf(children=[], text=tag, styles=[], url=None)
    if not isinstance(tag, bs4.element.Tag):
        print(f"Base: Cannot parse type {type(tag)}: {tag}")
        return None
    # now we assume it's a tag
    children = list(tag.children)
    if tag.name == "a":
        assert len(children) == 0
        return AMLeaf([], tag.text, [], tag.attrs["href"])

    # potentially recursive cases
    parsed_children = [_parse_soup_tag(c) for c in children]
    parsed_children = [c for c in parsed_children if c is not None]
    if len(parsed_children) == 0:
        return None

    if tag.name in ["strong", "b"]:
        if len(children) == 0:
            return AMLeaf(children=[], text=tag.text, styles=["bold"], url=None)
        else:
            return AMContainer(children=parsed_children, styles=["bold"])
    if tag.name in ["em", "i"]:
        if len(children) == 0:
            return AMLeaf(children=[], text=tag.text, styles=["italic"], url=None)
        else:
            return AMContainer(children=parsed_children, styles=["italic"])
    if tag.name in ["u"]:
        if len(children) == 0:
            return AMLeaf(children=[], text=tag.text, styles=["underline"], url=None)
        else:
            return AMContainer(children=parsed_children, styles=["underline"])
    if tag.name in ["code"]:
        if len(children) == 0:
            return AMLeaf(children=[], text=tag.text, styles=["code"], url=None)
        else:
            return AMContainer(children=parsed_children, styles=["code"])

    if tag.name in ["body", "span", "div", "p", "html", "[document]", "head", "li"]:
        # TODO (ian): parse styles and work out where to store them (span or leaf?)
        if len(parsed_children) == 1:
            return parsed_children[0]
        return AMContainer(children=parsed_children, styles=[])
    if tag.name == "ul":
        return AMList(children=parsed_children, ordered=False)
    if tag.name == "ol":
        return AMList(children=parsed_children, ordered=True)

    print(f"End: Cannot parse tag {tag.name} with attrs {tag.attrs} and children {tag.children}")
    return None

def parse_obsidian_markdown(text):
    """Parse obsidian-flavored markdown (in particular, lists) into HTML.
    
    (Help from https://claude.ai/chat/63a0feed-2065-4216-90d5-b10232326d5b)"""
    preprocessed_text = preprocess_obsidian_markdown(text)
    html = markdown.markdown(preprocessed_text, extensions=["sane_lists"])
    return html

def preprocess_obsidian_markdown(text):
    # Regular expression pattern to match text followed by a list without a newline
    pattern = re.compile(r'(.*)\n((?:[*+-] .*(?:\n|$))+)', re.MULTILINE)

    # Replace matched patterns with text followed by two newlines and the list
    def replace_unordered(match):
        return f'{match.group(1)}\n\n{match.group(2)}'

    processed_text = pattern.sub(replace_unordered, text)

    pattern = re.compile(r'(.*)\n((?:\d+\. .*(?:\n|$))+)', re.MULTILINE)

    # Replace matched patterns with text followed by two newlines and the list
    def replace_ordered(match):
        return f'{match.group(1)}\n\n{match.group(2)}'

    processed_text = pattern.sub(replace_ordered, processed_text)

    return processed_text


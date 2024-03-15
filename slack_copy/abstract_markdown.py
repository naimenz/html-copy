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
            text = parse_obsidian_md(text)
            print(text)
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


def _add_newlines_before_lists(text: str) -> str:
    """
    Add a newline before each bulleted list in a string.
    """
    # Regular expression to find list items
    # This matches lines starting with a list item that do not have a preceding newline.
    list_item_pattern = re.compile(r"(?<!\n)(\n- |\n\d+\. )")
    # Insert a newline before list items that don't already have one
    # The \1 in the replacement string refers to the matched list item prefix (- or a digit followed by .), preserving it.
    processed_content = re.sub(list_item_pattern, r"\n\1", text)
    return processed_content

    # # for each line in the text, if it is the first line of a list, add a newline before it
    # new_text = ""
    # previous_starts_with_list = False
    # for i, line in enumerate(text.split("\n")):
    #     line_starts_with_list = line.strip().startswith("-") or line.strip().startswith("1.")
    #     if not previous_starts_with_list and line_starts_with_list:
    #         new_text += "\n"
    #     new_text += line + "\n"
    #     previous_starts_with_list = line_starts_with_list
    # return new_text


def parse_obsidian_md(text: str) -> str:
    """
    Parse a string in Obsidian's markdown format to html.
    (from https://github.com/mfarragher/obsidiantools/blob/main/obsidiantools/md_utils.py)
    """
    html = markdown.markdown(
        text,
        output_format="html",
        extensions=[
            "pymdownx.arithmatex",
            "pymdownx.superfences",
            "pymdownx.mark",
            "pymdownx.tilde",
            "pymdownx.saneheaders",
            "footnotes",
            "sane_lists",
            "tables",
        ],
        extension_configs={"pymdownx.tilde": {"subscript": False}},
    )
    return html

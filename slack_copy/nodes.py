
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal
import typing

Style = Literal["bold", "italic", "underline", "strikethrough", "code"]
styles: tuple[Style, ...] = typing.get_args(Style)

@dataclass
class AMNode(ABC):
    """
    Node in an AbstractMarkdownTree.
    """
    children: list["AMNode"]

    @abstractmethod
    def to_html(self) -> str:
        pass

@dataclass
class AMLeaf(AMNode):
    """
    Leaf node in an AbstractMarkdownTree.

    If a url is given, the text should be a hyperlink.
    """
    text: str
    styles: list[Style]
    url: str | None = None
    
    def __post_init__(self):
        assert self.children == [], "Leaf nodes cannot have children"

    def to_html(self) -> str:
        if self.url is not None:
            return f'<a href="{self.url}">{self.text}</a>'
        return self.text

@dataclass
class AMContainer(AMNode):
    """
    Container node in an AbstractMarkdownTree.

    Similar to div, span, body, etc in HTML; basically a container for other nodes.

    If a url is given, the container should be a hyperlink tag (<a>).
    """
    styles: list[Style]
    url: str | None = None
    ql_indent: int = 0

    def to_html(self) -> str:
        tag = "a" if self.url is not None else "span"
        content = "".join(child.to_html() for child in self.children)
        if self.url is not None:
            return f'<a href="{self.url}">{content}</a>'
        else:
            return f'<span>{content}</span>'

@dataclass
class AMList(AMNode):
    """
    List node in an AbstractMarkdownTree.

    Similar to ul or ol in HTML.

    Args:
        ordered: Whether the list is ordered (True) or unordered (False).
        data_indent: The indentation level of the list (only used when parsing
            Slack HTML, which uses margin-left for indentation instead of nested
            lists).

    """
    ordered: bool
    data_indent: int | None = None


    def to_html(self) -> str:
        list_type = "ol" if self.ordered else "ul"
        list_html = ""
        # generate html iteratively (to handle nested lists)
        for child in self.children:
            child_html = child.to_html()
            if isinstance(child, AMList):
                list_html += f"{child_html}"
            else:
                list_html += f"<li>{child_html}</li>"
        return f"<{list_type}>{list_html}</{list_type}>"

# @dataclass
# class AMListElement(AMNode):
#     """
#     Element in a list node in an AbstractMarkdownTree.

#     Similar to li in HTML.
#     """
#     ql_indent: int

#     def to_html(self) -> str:
#         return "".join(child.to_html() for child in self.children)
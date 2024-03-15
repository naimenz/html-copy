
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
    url: str | None
    
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
    """
    styles: list[Style]

    def to_html(self) -> str:
        return f"<span>{''.join(child.to_html() for child in self.children)}</span>"

@dataclass
class AMList(AMNode):
    """
    List node in an AbstractMarkdownTree.

    Similar to ul or ol in HTML.
    """
    ordered: bool

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
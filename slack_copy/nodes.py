
from abc import ABC
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


@dataclass
class AMContainer(AMNode):
    """
    Container node in an AbstractMarkdownTree.

    Similar to div, span, body, etc in HTML; basically a container for other nodes.
    """
    styles: list[Style]

@dataclass
class AMList(AMNode):
    """
    List node in an AbstractMarkdownTree.

    Similar to ul or ol in HTML.
    """
    ordered: bool
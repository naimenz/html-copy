from abc import ABC
from dataclasses import dataclass
import typing
from typing import Literal, Union

Style = Literal["bold", "italic", "underline", "strikethrough", "code"]
styles: tuple[Style, ...] = typing.get_args(Style)

class AbstractMarkdownTree:
    """
    Abstract representation of markdown content.

    Represents a markdown file in a way that is independent of the actual implementation.
    This way we can convert to and from different formats (e.g. Slack, Obsidian, etc.)
    """

    def __init__(self, content: dict) -> None:
        raise NotImplementedError

    @staticmethod
    def from_obsidian(text: str) -> "AbstractMarkdownTree":
        raise NotImplementedError

    def to_obsidian(self) -> str:
        raise NotImplementedError

    @staticmethod
    def from_slack(text: str) -> "AbstractMarkdownTree":
        raise NotImplementedError

    def to_slack(self) -> str:
        raise NotImplementedError

    @staticmethod
    def from_gdocs(text: str) -> "AbstractMarkdownTree":
        raise NotImplementedError

    def to_gdocs(self) -> str:
        raise NotImplementedError

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


class AMSpan(AMNode):
    """
    Span node in an AbstractMarkdownTree.

    Similar to div in HTML; basically a container for other nodes.
    """

class AMList(AMNode):
    """
    List node in an AbstractMarkdownTree.

    Similar to ul or ol in HTML.
    """
    ordered: bool
    children: list[AMNode]
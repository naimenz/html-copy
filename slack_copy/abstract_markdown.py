class AbstractMarkdown:
    """
    Abstract representation of markdown content.

    Represents a markdown file in a way that is independent of the actual implementation.
    This way we can convert to and from different formats (e.g. Slack, Obsidian, etc.)
    """

    def __init__(self, content: dict) -> None:
        raise NotImplementedError

    @staticmethod
    def from_obsidian(text: str) -> "AbstractMarkdown":
        raise NotImplementedError

    def to_obsidian(self) -> str:
        raise NotImplementedError

    @staticmethod
    def from_slack(text: str) -> "AbstractMarkdown":
        raise NotImplementedError

    def to_slack(self) -> str:
        raise NotImplementedError

    @staticmethod
    def from_gdocs(text: str) -> "AbstractMarkdown":
        raise NotImplementedError

    def to_gdocs(self) -> str:
        raise NotImplementedError

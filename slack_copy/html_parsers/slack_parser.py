
from typing_extensions import override

from bs4 import PageElement

from slack_copy.abstract_markdown import maybe_parse_slack_lists
from slack_copy.html_parsers.html_parser import HTMLParser
from slack_copy.nodes import AMNode


class SlackParser(HTMLParser):
    """Parse Slack-flavored HTML."""
    @override
    def get_parsed_children(self, children: list[PageElement]) -> list[AMNode]:
        parsed_children = super().get_parsed_children(children)
        return maybe_parse_slack_lists(parsed_children)
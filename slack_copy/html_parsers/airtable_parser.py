
from typing import cast
from typing_extensions import override

from bs4.element import Tag

from slack_copy.abstract_markdown import get_airtable_ql_indent, maybe_parse_airtable_list, maybe_parse_slack_lists
from slack_copy.html_parsers.html_parser import HTMLParser
from slack_copy.nodes import AMList, AMListElement, AMNode


class AirtableParser(HTMLParser):
    """Parse Airtable-flavored HTML."""
    @override
    def parse_li_tag(self, tag, parsed_children: list[AMNode]) -> AMListElement:
        # Pre-process the children in the case that we have Airtable lists.
        ql_indent = get_airtable_ql_indent(tag)
        return AMListElement(children=parsed_children, ql_indent=ql_indent)

    @override
    def parse_parent_list_tag(self, tag: Tag, parsed_children: list[AMNode]) -> AMList:
        parent = super().parse_parent_list_tag(tag, parsed_children)
        assert all(isinstance(c, AMListElement) for c in parsed_children)
        list_children = cast(list[AMListElement], parsed_children)
        # Modifies the parent in-place
        parent = maybe_parse_airtable_list(parent, list_children)
        return parent
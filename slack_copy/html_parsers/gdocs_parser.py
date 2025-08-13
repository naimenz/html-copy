
from collections import deque
from typing import cast
from typing_extensions import override

from bs4.element import Tag

from slack_copy.html_parsers.html_parser import HTMLParser
from slack_copy.nodes import AMContainer, AMNode, AMSpan


class GDocsParser(HTMLParser):
    """Parse Google Docs-flavored HTML."""

    def parse_p_tag(self, tag: Tag, parsed_children: list[AMNode]) -> AMNode:
        """Remove <p> tags for gdocs.
        
        GDocs seems to add unnecessary <p> tags that add whitespace when pasted
        into other text editors. So instead of returning a paragraph, we return
        a container.
        """
        # HACK: Just drop the container, if there's a single child.
        if len(parsed_children) == 1:
            return parsed_children[0]
        # HACK: Turn the container into a span.
        return AMSpan(children=parsed_children, styles=[])
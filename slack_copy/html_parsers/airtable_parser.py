
from collections import deque
from typing import cast
from typing_extensions import override

from bs4.element import Tag

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


def maybe_parse_airtable_list(parent: AMList, children: list[AMListElement]) -> AMList:
    """Parse Airtable lists into nested lists if necessary.

    Modifies the parent in-place. 

    Args:
        children: The children to parse.
    """
    if len(children) <= 1:
        # TODO(ian): Fix type hinting here.
        parent.children = children  # type: ignore
        return parent
    # TODO(ian): Separate out the logic for parsing Airtable lists.
    if not any(c.ql_indent > 0 for c in children):
        # TODO(ian): Fix type hinting here.
        parent.children = children  # type: ignore
        return parent
    
    current_list = parent
    stack = deque([current_list])
    previous_indent = 0

    for child in children:
        indent = child.ql_indent
        if indent == previous_indent:
            current_list.children.append(child)

        elif indent > previous_indent:
            assert indent == previous_indent + 1
            new_list = AMList(children=[child], ordered=parent.ordered, data_indent=parent.data_indent)
            current_list.children.append(new_list)
            stack.append(new_list)
            current_list = new_list
            previous_indent = indent

        # indent < previous_indent
        else:
            # Pop until we reach the right level of indentation
            for _ in range(previous_indent - indent):
                _ = stack.pop()
            current_list = stack[-1]
            current_list.children.append(child)
            previous_indent = indent
        
    return parent


def get_airtable_ql_indent(tag: Tag) -> int:
    """Get the ql-indent attribute from a tag, or 0 if it doesn't exist.

    Args:
        tag: The tag to get the ql-indent attribute from.
        
    Returns:
        The ql-indent attribute as an int.
    """
    # it's a class, so we need to split it
    ql_indent = tag.attrs.get("class")
    if ql_indent is None:
        return 0
    for class_name in ql_indent:
        if class_name.startswith("ql-indent-"):
            return int(class_name.split("-")[-1])
    raise ValueError(f"Could not find ql-indent in {ql_indent}")

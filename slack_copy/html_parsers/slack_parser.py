from typing import cast
from typing_extensions import override

from bs4 import PageElement, Tag

from slack_copy.html_parsers.html_parser import HTMLParser
from slack_copy.nodes import AMList, AMNode


class SlackParser(HTMLParser):
    """Parse Slack-flavored HTML."""

    @override
    def get_parsed_children(self, children: list[PageElement]) -> list[AMNode]:
        parsed_children = super().get_parsed_children(children)
        return maybe_parse_slack_lists(parsed_children)

    @override
    def parse_parent_list_tag(self, tag: Tag, parsed_children: list[AMNode]) -> AMList:
        data_indent = get_slack_data_indent(tag)
        ordered = tag.name == "ol"
        return AMList(children=parsed_children, ordered=ordered, data_indent=data_indent)


def maybe_parse_slack_lists(children: list[AMNode]) -> list[AMNode]:
    """Parse Slack lists into nested lists if necessary."""
    amlist_children = [c for c in children if isinstance(c, AMList)]
    # Handle the case where there is nothing to do, either because there are no
    # lists or because we're not parsing Slack lists (so data_indent is None).
    if len(amlist_children) == 0 or amlist_children[0].data_indent is None:
        return children

    return_list = []
    mixed_list = build_mixed_list(children)
    for group in mixed_list:
        if isinstance(group, list):
            assert all(isinstance(g, AMList) for g in group)
            casted_group = cast(list[AMList], group)
            return_list.append(parse_slack_lists(casted_group))
        # If it's not a list, it's just a single node.
        else:
            return_list.append(group)
    return return_list


def get_slack_data_indent(tag: Tag) -> int | None:
    """Get the data-indent attribute from a tag, or None if it doesn't exist.

    Args:
        tag: The tag to get the data-indent attribute from.

    Returns:
        The data-indent attribute (or similar) as an int.
    """

    data_indent = tag.attrs.get("data-indent")
    return int(data_indent) if data_indent is not None else None


def build_mixed_list(children: list[AMNode]) -> list[list[AMNode] | AMNode]:
    """Takes a list of AMNodes and returns a list that's a mix between
    AMNodes and lists of AMLists.

    For example, if the input is [A, B, C, D, E, F], where A, C, D, and E are
    AMLists, the output will be [[A], B, [C, D, E], F].
    """
    # Split the children into each consecutive group of lists and then
    # parse those and put them back.
    mixed_list = []
    current_group_of_amlists = []
    for child in children:
        if isinstance(child, AMList):
            current_group_of_amlists.append(child)
        else:
            if len(current_group_of_amlists) > 0:
                mixed_list.append(current_group_of_amlists)
                current_group_of_amlists = []
            mixed_list.append(child)

    # Add the last group of lists if it exists.
    if len(current_group_of_amlists) > 0:
        mixed_list.append(current_group_of_amlists)

    return mixed_list


def parse_slack_lists(siblings: list[AMList]) -> AMList:
    """Takes a list of Slack lists and reorders  them to be nested correctly.

    This is necessary because slack uses a flat list of nodes, with nesting
    displayed with margin-left. We need to convert this to a nested list.

    Args:
        siblings: A list of AMNodes at the same level. For now we assume that
            all nodes are list items.

    Returns:
        A list containing single AMList node that contains the nested list.

    Raises:
        ValueError: The list cannot be parsed. This can happen if the list
            starts with a more deeply nested item than the previous one.
    """
    if not all(isinstance(s, AMList) for s in siblings):
        raise ValueError("Expected only lists")
    if len(siblings) == 0:
        raise ValueError("Expected at least one list")
    if len(siblings) == 1:
        return siblings[0]

    n_siblings = len(siblings)
    # Loop over the siblings and try to nest them correctly.
    # It shouldn't take more than n_siblings to process them all.
    for _ in range(n_siblings):
        siblings = parse_slack_lists_once(siblings)

    if len(siblings) != 1:
        raise ValueError("Could not parse list")
    return siblings[0]


def parse_slack_lists_once(siblings: list[AMList]) -> list[AMList]:
    """Perform one iteration of fixing the nesting of Slack lists.

    We need to do this iteratively because we can don't know if the list
    will need to change more.

    TODO (ian): Work out a cleaner way to do this, maybe in one pass.

    Args:
        siblings: A list of 'n' AMList.

    Returns:
        A list of 'n-1' AMList at the same level, after two have been combined.

    Raises:
        ValueError: The list cannot be parsed. This can happen if the list
            starts with a more deeply nested item than the previous one.
    """
    siblings = siblings.copy()
    if len(siblings) == 1:
        # TODO (ian): Avoid returning here; we should not have
        # ended up in this function if it was len 1.
        return siblings

    assert siblings[0].data_indent is not None
    assert siblings[1].data_indent is not None
    if siblings[0].data_indent > siblings[1].data_indent:
        raise ValueError(
            "Cannot parse list where first list is more indented than second"
        )

    reversed_siblings = list(reversed(siblings))
    for i in range(len(siblings) - 1):
        sibling = reversed_siblings[i]
        # previous_sibling in this list is the sibling that comes *before* the
        # current one in the original list, but *after* in the reversed list.
        previous_sibling = reversed_siblings[i + 1]

        assert sibling.data_indent is not None
        assert previous_sibling.data_indent is not None

        # If the list is one more deeply nested than the previous one, make it a child.
        if sibling.data_indent == previous_sibling.data_indent + 1:
            previous_sibling.children.append(sibling)
            # Remove the sibling from the list to return, since it is now
            # a child of the previous sibling.
            reversed_siblings.pop(i)
            break

        # If they are at the same level, combine them.
        if sibling.data_indent == previous_sibling.data_indent:
            previous_sibling.children.extend(sibling.children)
            # Remove the sibling from the list to return, since it is now
            # combined with the previous sibling.
            reversed_siblings.pop(i)
            break

        # Otherwise, we just continue to the next pair.

    return list(reversed(reversed_siblings))

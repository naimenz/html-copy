import re
import typing
import markdown
from typing import Literal, cast

import bs4

from slack_copy.nodes import AMLeaf, AMList, AMNode, AMContainer

Style = Literal["bold", "italic", "underline", "strikethrough", "code"]
styles: tuple[Style, ...] = typing.get_args(Style)


class AbstractMarkdownTree:
    """
    Abstract representation of markdown content.

    Represents a markdown file in a way that is independent of the actual implementation.
    This way we can convert to and from different formats (e.g. Slack, Obsidian, etc.)
    """

    def __init__(self, root: AMNode) -> None:
        self.root = root

    def to_html(self) -> str:
        return self.root.to_html()

    @staticmethod
    def from_obsidian(text: str, is_html: bool = True) -> "AbstractMarkdownTree":
        if not is_html:
            text = parse_obsidian_markdown(text)
        soup = bs4.BeautifulSoup(text, "lxml")
        root = _parse_soup_tag(soup)
        assert root is not None
        return AbstractMarkdownTree(root)

    def to_obsidian(self) -> str:
        raise NotImplementedError

    @staticmethod
    def from_slack(text: str) -> "AbstractMarkdownTree":
        soup = bs4.BeautifulSoup(text, "lxml")
        root = _parse_soup_tag(soup)
        assert root is not None
        return AbstractMarkdownTree(root)

    def to_slack(self) -> str:
        raise NotImplementedError

    @staticmethod
    def from_gdocs(text: str) -> "AbstractMarkdownTree":
        soup = bs4.BeautifulSoup(text, "lxml")
        root = _parse_soup_tag(soup)
        assert root is not None
        return AbstractMarkdownTree(root)

    def to_gdocs(self) -> str:
        raise NotImplementedError


def _parse_soup_tag(tag: bs4.element.PageElement) -> AMNode | None:
    """
    Parse HTML and return an AbstractMarkdownTree.
    """
    # base cases
    if isinstance(tag, bs4.element.NavigableString):
        return AMLeaf(children=[], text=tag, styles=[], url=None)
    if not isinstance(tag, bs4.element.Tag):
        print(f"Base: Cannot parse type {type(tag)}: {tag}")
        return None
    # now we assume it's a tag
    children = list(tag.children)

    # potentially recursive cases
    parsed_children = [_parse_soup_tag(c) for c in children]
    parsed_children = [c for c in parsed_children if c is not None]
    if len(parsed_children) == 0:
        return None
    
    # TODO (ian): Move slack-specific parsing somewhere else.
    parsed_children = maybe_parse_slack_lists(parsed_children)

    if tag.name == "a":
        if len(children) == 0:
            return AMLeaf(children=[], text=tag.text, styles=[], url=tag.attrs["href"])
        else:
            return AMContainer(children=parsed_children, styles=[], url=tag.attrs["href"])

    if tag.name in ["strong", "b"]:
        if len(children) == 0:
            return AMLeaf(children=[], text=tag.text, styles=["bold"], url=None)
        else:
            return AMContainer(children=parsed_children, styles=["bold"])
    if tag.name in ["em", "i"]:
        if len(children) == 0:
            return AMLeaf(children=[], text=tag.text, styles=["italic"], url=None)
        else:
            return AMContainer(children=parsed_children, styles=["italic"])
    if tag.name in ["u"]:
        if len(children) == 0:
            return AMLeaf(children=[], text=tag.text, styles=["underline"], url=None)
        else:
            return AMContainer(children=parsed_children, styles=["underline"])
    if tag.name in ["code"]:
        if len(children) == 0:
            return AMLeaf(children=[], text=tag.text, styles=["code"], url=None)
        else:
            return AMContainer(children=parsed_children, styles=["code"])

    if tag.name in ["body", "span", "div", "p", "html", "[document]", "head"]:
        # TODO (ian): parse styles and work out where to store them (span or leaf?)
        if len(parsed_children) == 1:
            return parsed_children[0]
        return AMContainer(children=parsed_children, styles=[])
    if tag.name == "li":
        # Pre-process the children in the case that we have Airtable lists.
        ql_indent = get_airtable_ql_indent(tag)
        if len(parsed_children) == 1:
            return parsed_children[0]
        return AMContainer(children=parsed_children, styles=[], ql_indent=ql_indent)
    if tag.name == "ul":
        data_indent = get_slack_data_indent(tag)
        parsed_children = maybe_parse_airtable_list(parsed_children)
        return AMList(children=parsed_children, ordered=False, data_indent=data_indent)
    if tag.name == "ol":
        data_indent = get_slack_data_indent(tag)
        parsed_children = maybe_parse_airtable_list(parsed_children)
        return AMList(children=parsed_children, ordered=True, data_indent=data_indent)

    print(f"End: Cannot parse tag {tag.name} with attrs {tag.attrs} and children {tag.children}")
    return None

def maybe_parse_airtable_list(children: list[AMNode], ordered: bool) -> list[AMNode]:
    """Parse Airtable lists into nested lists if necessary.
    
    Args:
        children: The children to parse.
    """
    if len(children) <= 1:
        return children
    if not any(getattr(c, "ql_indent", 0) > 0 for c in children):
        return children
    
    children_to_return = []
    current_parent_lists: dict[int, AMList] = {}
    prev_ql_indent = 0
    prev_child = None
    for i, child in enumerate(children):
        assert isinstance(child, AMContainer)
        if child.ql_indent == 0:
            children_to_return.append(child)
            continue

        assert child.ql_indent <= i
        # Make a new list if the next is more indented.
        if child.ql_indent > prev_ql_indent:
            if child.ql_indent != prev_ql_indent + 1:
                raise ValueError("Currently can't handle multiple indents")
            
            parent = current_parent_lists.get(child.ql_indent)
            if parent is None:
                parent = AMList(children=[], ordered=ordered, data_indent=None)
                current_parent_lists[prev_ql_indent] = parent
            parent.children.append(child)
            prev_ql_indent = child.ql_indent
        elif child.ql_indent < prev_ql_indent:
            parent = current_parent_lists.get(child.ql_indent)
            if parent is None:
                raise ValueError("No parent found")
            parent.children.append(child)
            prev_ql_indent = child.ql_indent




def get_airtable_ql_indent(tag: bs4.element.Tag) -> int:
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

def get_slack_data_indent(tag: bs4.element.Tag) -> int | None:
    """Get the data-indent attribute from a tag, or None if it doesn't exist.

    Args:
        tag: The tag to get the data-indent attribute from.
        
    Returns:
        The data-indent attribute (or similar) as an int.
    """


    data_indent = tag.attrs.get("data-indent")
    return int(data_indent) if data_indent is not None else None

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

def parse_obsidian_markdown(text):
    """Parse obsidian-flavored markdown (in particular, lists) into HTML.

    (Help from https://claude.ai/chat/63a0feed-2065-4216-90d5-b10232326d5b)"""
    preprocessed_text = preprocess_obsidian_markdown(text)
    html = markdown.markdown(preprocessed_text, extensions=["sane_lists"])
    return html


def preprocess_obsidian_markdown(text):
    # Regular expression pattern to match text followed by a list without a newline
    pattern = re.compile(r"(.*)\n((?:[*+-] .*(?:\n|$))+)", re.MULTILINE)

    # Replace matched patterns with text followed by two newlines and the list
    def replace_unordered(match):
        return f"{match.group(1)}\n\n{match.group(2)}"

    processed_text = pattern.sub(replace_unordered, text)

    pattern = re.compile(r"(.*)\n((?:\d+\. .*(?:\n|$))+)", re.MULTILINE)

    # Replace matched patterns with text followed by two newlines and the list
    def replace_ordered(match):
        return f"{match.group(1)}\n\n{match.group(2)}"

    processed_text = pattern.sub(replace_ordered, processed_text)

    # Add a newline between the end of the list and continued text
    # (from https://claude.ai/chat/78f86edb-cd82-43b4-bae2-ea891f9a1f67)
    pattern = r"(?m)^(?:(?:\s*\d+\.|\s*-)\s+.*(?:\n(?:\s*\d+\.|\s*-)\s+.*)*)\n(?!\s*(?:\d+\.|-)\s)"
    processed_text = re.sub(pattern, r"\g<0>\n", processed_text)

    return processed_text

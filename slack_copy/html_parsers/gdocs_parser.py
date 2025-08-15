from bs4.element import Tag

from slack_copy.html_parsers.html_parser import HTMLParser
from slack_copy.nodes import AMList, AMNode, AMSpan, AMWrapper


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
    
    def parse_strong_tag(self, tag: Tag, parsed_children: list[AMNode]) -> AMNode:
        """Remove <strong> or <b> tags for gdocs.
        
        GDocs puts <b> around the whole sentence(?) whenever there's bold text.
        It then uses font-weight on <span> to actually make things bold/not bold.
        Thus we just return the child, and we'll parse bold from attributes of the
        <span>.
        """
        return AMSpan(children=parsed_children, styles=[])

    def parse_span_tag(self, tag: Tag, parsed_children: list[AMNode]) -> AMSpan:
        """Parse the attributes of a gdocs <span> tag.
        
        """
        span = super().parse_span_tag(tag, parsed_children)
        tag_style = tag.attrs.get("style", "")
        if "font-weight:700;" in tag_style:
            span = AMSpan(children=parsed_children, styles=span.styles + ["bold"])
        if "monospace" in tag_style and "color:#188038" in tag_style:
            span = AMSpan(children=parsed_children, styles=span.styles + ["code"])
        
        return span

    def parse_parent_list_tag(self, tag: Tag, parsed_children: list[AMNode]) -> AMList:
        """Parse the children of a gdocs list element.
        
        """
        return parse_gdocs_list(super().parse_parent_list_tag(tag, parsed_children))

def parse_gdocs_list(gdocs_list: AMList) -> AMList:
    """Parse the children of a gdocs list element.
    
    Google Docs has bare <ul> as children of other <ul> tags to indicate nesting.
    This does not play well with Obsidian, which renders newlines in this case.
    What we need instead is to make the <ul> tag part of the previous <li> tag.
    (And to remove unnecessary <p> tags, where present, done separately.)

    Procedure: 
    - If the first element is a nested list, then we say that's invalid
    and raise an error.
    - Otherwise, we combine nested lists into the previous <li> tag.
    - We then return the list.

    Args:
        gdocs_list: The list to parse.

    Returns:
        The parsed list.
    """
    children = gdocs_list.children
    if len(children) == 0:
        raise ValueError("Expected at least one child")
    if len(children) == 1:
        return gdocs_list
    
    # If the first element is a nested list, then we say that's invalid
    # and raise an error.
    if isinstance(children[0], AMList):
        raise ValueError("Expected a list, got a nested list")
    
    # Otherwise, we combine nested lists into the previous <li> tag.
    new_children = []
    previous_li = children[0]
    for child in children[1:]:
        if isinstance(child, AMList):
            previous_li = AMWrapper(children=[previous_li, child])
        else:
            new_children.append(previous_li)
            previous_li = child
    new_children.append(previous_li)
    new_list = AMList(children=new_children, ordered=gdocs_list.ordered, data_indent=gdocs_list.data_indent)
    return new_list
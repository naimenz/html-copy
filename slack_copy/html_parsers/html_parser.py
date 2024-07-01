import bs4
from slack_copy.nodes import STYLES, AMLeaf, AMNode, AMSpan, AMParagraph, AMContainer, AMListElement, AMList
from bs4.element import PageElement, NavigableString, Tag

class HTMLParser:
    """The basic HTML parser class, with default parsing for each tag.
    
    Subclasses should override specific tag methods to change the behavior.
    """

    def parse(self, text: str) -> AMNode:
        root_tag = bs4.BeautifulSoup(text, "lxml")
        root_node = self.recursive_parse(root_tag)
        if root_node is None:
            raise ValueError(f"Couldn't parse root tag {root_tag}")
        return root_node

    def recursive_parse(self, tag: PageElement) -> AMNode | None:
        """Parse HTML and return an AbstractMarkdownTree."""
        # Base cases
        if isinstance(tag, NavigableString):
            return self.parse_navigable_string(tag)

        if not isinstance(tag, Tag):
            print(f"Base: Cannot parse type {type(tag)}: {tag}")
            return None

        # Now we assume it's a tag.
        children = list(tag.children)

        # Potentially recursive cases:
        parsed_children = self.get_parsed_children(children)
        if len(parsed_children) == 0:
            return None
        

        if tag.name == "a":
            return self.parse_a_tag(tag, parsed_children)
        if tag.name in ["strong", "b"]:
            return self.parse_strong_tag(tag, parsed_children)
        if tag.name in ["em", "i"]:
            return self.parse_em_tag(tag, parsed_children)
        if tag.name in ["s"]:
            return self.parse_s_tag(tag, parsed_children)
        if tag.name in ["u"]:
            return self.parse_u_tag(tag, parsed_children)
        if tag.name in ["code"]:
            return self.parse_code_tag(tag, parsed_children)
        if tag.name in ["span"]:
            return self.parse_span_tag(tag, parsed_children)
        if tag.name in ["p"]:
            return self.parse_p_tag(tag, parsed_children)
        if tag.name in ["body", "span", "div", "html", "[document]", "head"]:
            return self.parse_container_tag(tag, parsed_children)
        if tag.name == "li":
            return self.parse_li_tag(tag, parsed_children)
        if tag.name in ["ul", "ol"]:
            return self.parse_parent_list_tag(tag, parsed_children)

        print(f"End: Cannot parse tag {tag.name} with attrs {tag.attrs} and children {list(tag.children)}")
        return None

    def parse_navigable_string(self, tag: NavigableString) -> AMLeaf:
        return AMLeaf(children=[], text=tag, styles=[], url=None)

    def get_parsed_children(self, children: list[PageElement]) -> list[AMNode]:
        parsed_children = [self.recursive_parse(c) for c in children]
        return [c for c in parsed_children if c is not None]

    def parse_a_tag(self, tag: Tag, parsed_children: list[AMNode]) -> AMNode:
        if len(parsed_children) == 0:
            return AMLeaf(children=[], text=tag.text, styles=[], url=tag.attrs["href"])
        else:
            return AMSpan(children=parsed_children, styles=[], url=tag.attrs["href"])

    def parse_strong_tag(self, tag: Tag, parsed_children: list[AMNode]) -> AMNode:
        if len(parsed_children) == 0:
            return AMLeaf(children=[], text=tag.text, styles=["bold"], url=None)
        else:
            return AMSpan(children=parsed_children, styles=["bold"])

    def parse_em_tag(self, tag: Tag, parsed_children: list[AMNode]) -> AMNode:
        if len(parsed_children) == 0:
            return AMLeaf(children=[], text=tag.text, styles=["italic"], url=None)
        else:
            return AMSpan(children=parsed_children, styles=["italic"])

    def parse_s_tag(self, tag: Tag, parsed_children: list[AMNode]) -> AMNode:
        if len(parsed_children) == 0:
            return AMLeaf(children=[], text=tag.text, styles=["strikethrough"], url=None)
        else:
            return AMSpan(children=parsed_children, styles=["strikethrough"])

    def parse_u_tag(self, tag: Tag, parsed_children: list[AMNode]) -> AMNode:
        if len(parsed_children) == 0:
            return AMLeaf(children=[], text=tag.text, styles=["underline"], url=None)
        else:
            return AMSpan(children=parsed_children, styles=["underline"])

    def parse_code_tag(self, tag: Tag, parsed_children: list[AMNode]) -> AMNode:
        if len(parsed_children) == 0:
            return AMLeaf(children=[], text=tag.text, styles=["code"], url=None)
        else:
            return AMSpan(children=parsed_children, styles=["code"])

    def parse_span_tag(self, tag: Tag, parsed_children: list[AMNode]) -> AMSpan:
        # TODO(ian): Parse styles and work out where to store them (span or leaf?)
        for style in STYLES:
            if style in tag.attrs.get("style", ""):
                return AMSpan(children=parsed_children, styles=[style])
        return AMSpan(children=parsed_children, styles=[])

    def parse_p_tag(self, tag: Tag, parsed_children: list[AMNode]) -> AMParagraph:
        return AMParagraph(children=parsed_children, styles=[])

    def parse_container_tag(self, tag: Tag, parsed_children: list[AMNode]) -> AMNode:
        # TODO (ian): parse styles and work out where to store them (span or leaf?)
        if len(parsed_children) == 1:
            return parsed_children[0]
        return AMContainer(children=parsed_children, styles=[])

    def parse_li_tag(self, tag: Tag, parsed_children: list[AMNode]) -> AMListElement:
        return AMListElement(children=parsed_children)

    def parse_parent_list_tag(self, tag: Tag, parsed_children: list[AMNode]) -> AMList:
        ordered = tag.name == "ol"
        return AMList(children=parsed_children, ordered=ordered)
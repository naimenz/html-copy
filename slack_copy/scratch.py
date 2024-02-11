# %%
import json

import markdown
from slack_copy.abstract_markdown import AbstractMarkdownTree
from slack_copy.examples.basic import BASIC_EXAMPLE
import bs4
import dataclasses
soup = bs4.BeautifulSoup(BASIC_EXAMPLE["gdocs"], "lxml")

gdocs_amtree = AbstractMarkdownTree.from_gdocs(BASIC_EXAMPLE["gdocs"])
gdocs_string = dataclasses.asdict(gdocs_amtree.root)
slack_amtree = AbstractMarkdownTree.from_slack(BASIC_EXAMPLE["slack"])
slack_string = dataclasses.asdict(slack_amtree.root)
obsidian_amtree = AbstractMarkdownTree.from_obsidian(BASIC_EXAMPLE["obsidian_html"])
obsidian_string = dataclasses.asdict(obsidian_amtree.root)
obsidian_md_amtree = AbstractMarkdownTree.from_obsidian(BASIC_EXAMPLE["obsidian_plain"], is_html=False)
obsidian_md_string = dataclasses.asdict(obsidian_md_amtree.root)

obsidian_2 = """
Here’s an example message I’d like to copy:

- Some *bullet* points
	- Including nested

2. Maybe some **numbered** bullet points
	1. Also nested
	2. I would also like to include some `code snippets` if possible
""".strip()
# print(markdown.markdown(BASIC_EXAMPLE["obsidian_plain"]))
print(markdown.markdown(obsidian_2))
amtree = AbstractMarkdownTree.from_obsidian(obsidian_2, is_html=False)
print(json.dumps(dataclasses.asdict(amtree.root), indent=2))

raise ValueError
# print(json.dumps(slack_string, indent=2))
print(json.dumps(obsidian_string, indent=2))
print("===================")
print(json.dumps(obsidian_md_string, indent=2))
# print(gdocs_string == slack_string)

# %%

# root = next(iter(soup))
# for tag in soup.descendants:
#     if tag.name == "span":
#         print(tag)
#     if not isinstance(tag, bs4.element.Tag):
#         continue
#     # print(tag.attrs)
#     tag.attrs = {}
    # print()
# for i, child in enumerate(root.children):
#     for j, c in enumerate(child.children):
#         print(f"{i = }, {j = }, {c = }")
#         c.attrs = None
#         print(c.attrs)
# print(soup.prettify())
# print(soup.prettify())
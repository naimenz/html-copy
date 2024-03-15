# %%
import json

from pprint import pprint
import markdown
from slack_copy.abstract_markdown import AbstractMarkdownTree
from slack_copy.examples.basic import BASIC_EXAMPLE
import bs4
import dataclasses
soup = bs4.BeautifulSoup(BASIC_EXAMPLE["gdocs"], "lxml")

obsidian_md_amtree = AbstractMarkdownTree.from_obsidian(BASIC_EXAMPLE["obsidian_plain"], is_html=False)
obsidian_md_string = dataclasses.asdict(obsidian_md_amtree.root)
# pprint(obsidian_md_string)
obsidian_md_html = obsidian_md_amtree.to_html()
print(obsidian_md_html)










# gdocs_amtree = AbstractMarkdownTree.from_gdocs(BASIC_EXAMPLE["gdocs"])
# gdocs_string = dataclasses.asdict(gdocs_amtree.root)
# slack_amtree = AbstractMarkdownTree.from_slack(BASIC_EXAMPLE["slack"])
# slack_string = dataclasses.asdict(slack_amtree.root)
# obsidian_amtree = AbstractMarkdownTree.from_obsidian(BASIC_EXAMPLE["obsidian_html"])
# obsidian_string = dataclasses.asdict(obsidian_amtree.root)
# obsidian_md_amtree = AbstractMarkdownTree.from_obsidian(BASIC_EXAMPLE["obsidian_plain"], is_html=False)
# obsidian_md_string = dataclasses.asdict(obsidian_md_amtree.root)

# # pprint(f"gdocs_string = ")
# # pprint(gdocs_string)
# reconstructed_gdocs_html = gdocs_amtree.to_html()
# # reconstructed_obsidian_md_html = obsidian_md_amtree.to_html()
# # print(BASIC_EXAMPLE["obsidian_html"])
# reconstructed_obsidian_html = obsidian_amtree.to_html()
# pprint(obsidian_md_string)
# # pprint(f"reconstructed_gdocs_html = ")
# # print(reconstructed_gdocs_html)
# # print(reconstructed_obsidian_html)
# # pprint(f"obsidian_string = ")
# # pprint(obsidian_string)
# # pprint(f"obsidian_md_string = ")
# # pprint(obsidian_md_string)
# # # %%

# # obsidian_2 = """
# # Here’s an example message I’d like to copy:

# # - Some *bullet* points
# # 	- Including nested

# # 2. Maybe some **numbered** bullet points
# # 	1. Also nested
# # 	2. I would also like to include some `code snippets` if possible
# # """.strip()
# # # print(markdown.markdown(BASIC_EXAMPLE["obsidian_plain"]))
# # print(markdown.markdown(obsidian_2))
# # amtree = AbstractMarkdownTree.from_obsidian(obsidian_2, is_html=False)
# # print(json.dumps(dataclasses.asdict(amtree.root), indent=2))

# # raise ValueError
# # # print(json.dumps(slack_string, indent=2))
# # print(json.dumps(obsidian_string, indent=2))
# # print("===================")
# # print(json.dumps(obsidian_md_string, indent=2))
# # print(gdocs_string == slack_string)

# # # %%

# # # root = next(iter(soup))
# # # for tag in soup.descendants:
# # #     if tag.name == "span":
# # #         print(tag)
# # #     if not isinstance(tag, bs4.element.Tag):
# # #         continue
# # #     # print(tag.attrs)
# # #     tag.attrs = {}
# #     # print()
# # # for i, child in enumerate(root.children):
# # #     for j, c in enumerate(child.children):
# # #         print(f"{i = }, {j = }, {c = }")
# # #         c.attrs = None
# # #         print(c.attrs)
# # # print(soup.prettify())
# # # print(soup.prettify())
# # # %%

# # %%

# # md_content = """
# # This is a paragraph.
# # - Item 1
# # - Item 2

# # 1. Numbered item 1
# # 2. Numbered item 2
# # """

# # # Convert Markdown to HTML
# # html_content = markdown.markdown(md_content)

# # print(html_content)
# # %%
# # import markdown

# # md_content = """
# # Here’s an example message I’d like to copy:

# # - Some *bullet* points
# #     - Including nested

# # 1. Maybe some **numbered** bullet points
# #     1. Also nested
# #     2. I would also like to include some `code snippets` if possible

# # And then back to regular text
# # """

# # # Convert Markdown to HTML
# # html_content = markdown.markdown(md_content)

# # print(html_content)
# # # %%

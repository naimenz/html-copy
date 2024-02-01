# %%
import json
from slack_copy.examples.basic import BASIC_EXAMPLE

loaded_example = json.loads(BASIC_EXAMPLE["obsidian"].replace("\n", "\\n"))
print(loaded_example["ops"])

# %%

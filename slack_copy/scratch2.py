import re
import markdown

def preprocess_markdown(text):
    # Regular expression pattern to match text followed by a list without a newline
    pattern = re.compile(r'(.*)\n((?:[*+-] .*(?:\n|$))+)', re.MULTILINE)

    # Replace matched patterns with text followed by two newlines and the list
    def replace_unordered(match):
        return f'{match.group(1)}\n\n{match.group(2)}'

    processed_text = pattern.sub(replace_unordered, text)

    pattern = re.compile(r'(.*)\n((?:\d+\. .*(?:\n|$))+)', re.MULTILINE)

    # Replace matched patterns with text followed by two newlines and the list
    def replace_ordered(match):
        return f'{match.group(1)}\n\n{match.group(2)}'

    processed_text = pattern.sub(replace_ordered, processed_text)

    # Handle nested bullets and ordered bullets
    # processed_text = re.sub(r'(?m)^(\s*)(\d+)\. ', r'\1\2\\. ', processed_text)
    # processed_text = re.sub(r'(?m)^(\s*)([*+-]) ', r'\1\2 ', processed_text)

    return processed_text

def parse_markdown(text):
    preprocessed_text = preprocess_markdown(text)
    html = markdown.markdown(preprocessed_text, extensions=['nl2br', "sane_lists"])
    return html

# Example usage
# Here's an example message I'd like to copy:
# - Some *bullet* points
#     - Including nested
markdown_text = '''
Here's an example message I'd like to copy:
- Some *bullet* points
    - Including nested
1. Maybe some **numbered** bullet points
    1. Also nested
    2. I would also like to include some `code snippets` if possible
'''

html_output = parse_markdown(markdown_text)
print(html_output)
import re

def insert_newline_after_lists(text):
    pattern = r'(?m)^(?:(?:\s*\d+\.|\s*-)\s+.*(?:\n(?:\s*\d+\.|\s*-)\s+.*)*)\n(?!\s*(?:\d+\.|-)\s)'
    return re.sub(pattern, r'\g<0>\n', text)

# Example usage
example1 = '''
    1. a list
        2. multiple elements
    And then back to regular text
'''

example2 = '''
    1. a different list
    - a list
        - multiple elements
    And then back to regular text
'''

print(insert_newline_after_lists(example1))
print(insert_newline_after_lists(example2))
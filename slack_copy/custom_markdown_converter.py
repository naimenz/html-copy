import re
from markdownify import MarkdownConverter

re_line_with_content = re.compile(r'^(.*)', flags=re.MULTILINE)

def custom_markdownify(html, **options):
    return CustomMarkdownConverter(**options).convert(html)

class CustomMarkdownConverter(MarkdownConverter):
    def convert_li(self, el, text, parent_tags):
        # handle some early-exit scenarios
        text = (text or '').strip()
        if not text:
            return "\n"

        # determine list item bullet character to use
        parent = el.parent
        if parent is not None and parent.name == 'ol':
            if parent.get("start") and str(parent.get("start")).isnumeric():
                start = int(parent.get("start"))
            else:
                start = 1
            bullet = '%s.' % (start + len(el.find_previous_siblings('li')))
        else:
            depth = -1
            while el:
                if el.name == 'ul':
                    depth += 1
                el = el.parent
            bullets = self.options['bullets']  # type: ignore (options is valid)
            bullet = bullets[depth % len(bullets)]
        bullet = bullet + ' '
        bullet_width = len(bullet)
        # HACK(ian): I need 4 spaces for Slack to render nested
        BULLET_INDENT_WIDTH = 4
        bullet_indent = ' ' * BULLET_INDENT_WIDTH

        # indent content lines by bullet width
        def _indent_for_li(match):
            line_content = match.group(1)
            return bullet_indent + line_content if line_content else ''
        text = re_line_with_content.sub(_indent_for_li, text)

        # insert bullet into first-line indent whitespace
        text = bullet + text[BULLET_INDENT_WIDTH:]

        return '%s\n' % text 
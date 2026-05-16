import html
import re

from django import template
from django.utils.safestring import mark_safe


register = template.Library()


FENCED_CODE_RE = re.compile(r'```([A-Za-z0-9_+.-]*)\n?(.*?)```', re.DOTALL)
INLINE_CODE_RE = re.compile(r'`([^`\n]+)`')
LINK_RE = re.compile(r'\[([^\]]+)\]\((https?://[^\s)]+)\)')


def _render_inline(text):
    code_spans = []

    def store_code(match):
        code_spans.append(f'<code>{html.escape(match.group(1))}</code>')
        return f'@@INLINECODE{len(code_spans) - 1}@@'

    text = INLINE_CODE_RE.sub(store_code, text)
    text = html.escape(text)

    def render_link(match):
        label = match.group(1)
        url = html.escape(match.group(2), quote=True)
        return f'<a href="{url}" target="_blank" rel="noopener noreferrer">{label}</a>'

    text = LINK_RE.sub(render_link, text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'__(.+?)__', r'<strong>\1</strong>', text)
    text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<em>\1</em>', text)
    text = re.sub(r'(?<!_)_(?!_)(.+?)(?<!_)_(?!_)', r'<em>\1</em>', text)

    for index, code in enumerate(code_spans):
        text = text.replace(f'@@INLINECODE{index}@@', code)

    return text


def _render_list(lines, ordered=False):
    tag = 'ol' if ordered else 'ul'
    items = []

    for line in lines:
        if ordered:
            item = re.sub(r'^\s*\d+\.\s+', '', line)
        else:
            item = re.sub(r'^\s*[-*+]\s+', '', line)
        items.append(f'<li>{_render_inline(item)}</li>')

    return f'<{tag}>{"".join(items)}</{tag}>'


def _render_blocks(text, code_blocks):
    html_blocks = []
    paragraph = []
    list_lines = []
    ordered_list = False

    def flush_paragraph():
        if paragraph:
            html_blocks.append(f'<p>{"<br>".join(_render_inline(line) for line in paragraph)}</p>')
            paragraph.clear()

    def flush_list():
        if list_lines:
            html_blocks.append(_render_list(list_lines, ordered_list))
            list_lines.clear()

    for line in text.split('\n'):
        stripped = line.strip()

        if not stripped:
            flush_paragraph()
            flush_list()
            continue

        code_match = re.fullmatch(r'@@CODEBLOCK(\d+)@@', stripped)
        if code_match:
            flush_paragraph()
            flush_list()
            html_blocks.append(code_blocks[int(code_match.group(1))])
            continue

        heading_match = re.match(r'^(#{1,6})\s+(.+)$', stripped)
        if heading_match:
            flush_paragraph()
            flush_list()
            level = len(heading_match.group(1))
            html_blocks.append(f'<h{level}>{_render_inline(heading_match.group(2))}</h{level}>')
            continue

        unordered_match = re.match(r'^\s*[-*+]\s+', line)
        ordered_match = re.match(r'^\s*\d+\.\s+', line)
        if unordered_match or ordered_match:
            flush_paragraph()
            current_ordered = bool(ordered_match)
            if list_lines and current_ordered != ordered_list:
                flush_list()
            ordered_list = current_ordered
            list_lines.append(line)
            continue

        flush_list()
        paragraph.append(stripped)

    flush_paragraph()
    flush_list()

    return ''.join(html_blocks)


@register.filter(name='markdown_content')
def markdown_content(value):
    text = str(value or '').replace('\r\n', '\n').replace('\r', '\n')
    code_blocks = []

    def store_code_block(match):
        language = html.escape(match.group(1).strip(), quote=True)
        code = html.escape(match.group(2).strip('\n'))
        class_attr = f' class="language-{language}"' if language else ''
        code_blocks.append(f'<pre><code{class_attr}>{code}</code></pre>')
        return f'\n\n@@CODEBLOCK{len(code_blocks) - 1}@@\n\n'

    text = FENCED_CODE_RE.sub(store_code_block, text)
    return mark_safe(_render_blocks(text, code_blocks))

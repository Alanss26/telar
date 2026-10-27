from markdown_it import MarkdownIt

# CommonMark plus the two GitHub extras people expect. Neither needs an extra dependency.
_parser = MarkdownIt("commonmark").enable(["table", "strikethrough"])


def render_markdown(text: str) -> str:
    # markdown-it-py annotates render() as returning Any.
    html: str = _parser.render(text)
    return html

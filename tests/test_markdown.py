from telar.markdown import render_markdown


def test_basic_markdown() -> None:
    assert render_markdown("# Hi\n\nSome *text*.") == "<h1>Hi</h1>\n<p>Some <em>text</em>.</p>\n"


def test_tables_are_enabled() -> None:
    html = render_markdown("| a | b |\n|---|---|\n| 1 | 2 |\n")
    assert "<table>" in html
    assert "<td>1</td>" in html


def test_strikethrough_is_enabled() -> None:
    assert "<s>gone</s>" in render_markdown("~~gone~~")

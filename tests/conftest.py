from pathlib import Path

import pytest

SITE_FILES = {
    "site.toml": 'title = "Test Site"\n',
    "templates/layouts/base.html": (
        "<!doctype html>\n"
        '<html lang="{{ site.language }}">\n'
        "<head><title>{{ page.title }} | {{ site.title }}</title></head>\n"
        "<body>\n"
        '{% include "partials/nav.html" %}\n'
        "<main>{% block main %}{% endblock %}</main>\n"
        "</body>\n"
        "</html>\n"
    ),
    "templates/layouts/page.html": (
        '{% extends "layouts/base.html" %}\n'
        "{% block main %}<h1>{{ page.title }}</h1>\n{{ page.content }}{% endblock %}\n"
    ),
    "templates/layouts/list.html": (
        '{% extends "layouts/base.html" %}\n'
        "{% block main %}<h1>{{ page.title }}</h1>\n<ul>\n"
        "{% for post in collections[page.collection] %}"
        '<li><a href="{{ post.url }}">{{ post.title }}</a></li>\n'
        "{% endfor %}</ul>{% endblock %}\n"
    ),
    "templates/partials/nav.html": '<nav><a href="/">Home</a></nav>\n',
    "content/index.md": "---\ntitle: Home\n---\nWelcome to **Telar**.\n",
    "content/blog/_index.md": "---\ntitle: Blog\n---\n",
    "content/blog/first.md": "---\ntitle: First\ndate: 2024-01-10\n---\nOne.\n",
    "content/blog/second.md": "---\ntitle: Second\ndate: 2024-03-05\n---\nTwo.\n",
    "content/blog/secret.md": "---\ntitle: Secret\ndraft: true\n---\nShh.\n",
    "static/css/style.css": "body { margin: 0; }\n",
}


@pytest.fixture
def site(tmp_path: Path) -> Path:
    """A small but complete site in a temp folder."""
    root = tmp_path / "site"
    for relative, text in SITE_FILES.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return root

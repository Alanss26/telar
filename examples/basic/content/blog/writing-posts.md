---
title: Writing posts
date: 2026-10-25
tags: [guide, markdown]
summary: Front matter fields and the Markdown you can use.
---

Every page starts with a front matter block between `---` lines:

```yaml
---
title: Writing posts
date: 2026-10-25
tags: [guide, markdown]
summary: Any extra field ends up in page.extra.
---
```

| Field    | Required | What it does                                        |
| -------- | -------- | --------------------------------------------------- |
| `title`  | yes      | The page title.                                     |
| `date`   | no       | Used to sort collections, newest first.             |
| `draft`  | no       | `true` keeps the page out of the build.             |
| `tags`   | no       | A list of strings.                                  |
| `layout` | no       | Template in `templates/layouts/` (default: `page`). |

The body is [CommonMark](https://commonmark.org/), plus tables and ~~strikethrough~~.

# Documentation Site

The documentation site is a standalone MkDocs project inside `docs-site/`.

Source repository:

<https://github.com/billzi2016/mmwave-fmcw-cascade-mimo-sensing-platform>

Published site:

<https://billzi2016.github.io/mmwave-fmcw-cascade-mimo-sensing-platform/>

## Directory Layout

```text
docs-site/
├── mkdocs.yml
├── requirements.txt
├── docs/
│   ├── en/
│   └── zh/
└── .github/
    └── workflows/
```

English content lives under `docs/en/`. Chinese content lives under `docs/zh/`. The two directories should keep the same relative page paths.

## Why This Structure

The folder-based language layout is easy to inspect and easy to maintain. A maintainer can open `docs/en/processing-pipeline.md` and immediately find the Chinese counterpart at `docs/zh/processing-pipeline.md`.

This also keeps the documentation separate from the radar code. The site can grow without changing the processing modules or the repository-level README files.

## What Is Tracked In Git

The source files under `docs-site/` are tracked in Git. The generated build output is not meant to be edited manually.

Tracked source files include:

- `mkdocs.yml`,
- `requirements.txt`,
- Markdown pages under `docs/en/` and `docs/zh/`,
- PRD files that describe the documentation-site requirements.

Ignored generated files include:

- `docs-site/site/`,
- Python cache directories such as `__pycache__/`,
- compiled Python cache files such as `*.pyc`.

This keeps the repository readable while still allowing the site to be rebuilt at any time.

## Maintenance Rule

When adding a new page:

1. Add the English page under `docs/en/`.
2. Add the Chinese page under `docs/zh/`.
3. Add the page once in `mkdocs.yml` navigation.
4. Keep headings and page order aligned across languages.

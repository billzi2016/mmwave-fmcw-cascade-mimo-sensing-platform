# Documentation Site

This directory contains the MkDocs documentation site for the radar sensing platform.

Published site:

https://billzi2016.github.io/mmwave-fmcw-cascade-mimo-sensing-platform/

Content is organized by language:

- `docs/en/`: English documentation
- `docs/zh/`: Chinese documentation

The site is configured with `mkdocs-static-i18n` and keeps the same page structure in both languages.

## Local Build

```bash
cd docs-site
python -m pip install -r requirements.txt
mkdocs serve
```

For a production build:

```bash
cd docs-site
mkdocs build --strict
```

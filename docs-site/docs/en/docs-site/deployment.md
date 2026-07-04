# Deployment Template

This site includes a GitHub Actions workflow template under:

```text
docs-site/.github/workflows/deploy-docs.yml
```

It is stored inside `docs-site/` because this task only changes the documentation-site folder.

## How To Enable It

To activate deployment in a real GitHub repository, copy the workflow file to:

```text
.github/workflows/deploy-docs.yml
```

The workflow builds the MkDocs site from `docs-site/` and deploys the generated static site to GitHub Pages.

## Trigger Policy

The template is designed to run only when documentation-site files change:

- `docs-site/**`
- the deployment workflow itself

This avoids rebuilding documentation when unrelated radar code changes.

## Build Command

The workflow uses:

```bash
mkdocs build --strict
```

Strict mode helps catch broken links, invalid navigation entries, and configuration errors early.

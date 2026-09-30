# Develop and preview documentation

Run these commands from a repository checkout. Python 3.10 or later and Git are required.

## Install for development

```console
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[test]'
```

## Run tests

Run the offline suite:

```console
python -m pytest tests --ignore=tests/test_cdse_integration.py
```

Run the live catalogue tests separately when network access is available:

```console
python -m pytest tests/test_cdse_integration.py
```

If you use Hatch, `hatch run dev:check` runs formatting checks, linting, typing, security checks, and the full test suite, including live integration tests. `hatch run dev:quality` runs only the static checks. The development environment does not define a `dev:test` script; use `hatch run dev:pytest tests` for tests alone.

## Build and preview the documentation

Install the documentation tools into your active environment:

```console
python -m pip install 'mkdocs<2' mkdocs-material mkdocs-mermaid2-plugin mkdocs-jupyter
python -m mkdocs build --strict
python -m mkdocs serve
```

Open the local address printed by `serve`. Notebook execution is disabled in the site build, so building documentation does not query CDSE. Run notebook cells manually when updating their examples and stored output.

## Choose the right documentation section

Follow [Diátaxis](https://diataxis.fr/) when adding a page:

- Put a guided learning exercise with an observable outcome in **Tutorials**.
- Put steps to accomplish a specific task in **How-to guides**.
- Put signatures, defaults, mappings, and precise limits in **Reference**.
- Put design context and reasons in **Explanation**.

Link related material instead of mixing all four purposes on one page. Add new pages to `nav` in `mkdocs.yaml`, check examples against the source, and run a strict build before submitting changes.

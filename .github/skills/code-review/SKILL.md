---
name: code-review
description: 'Review code against base_project conventions. Use for checking style, type hints, docstrings, config patterns, test coverage before merging or committing.'
argument-hint: 'Files or scope to review'
---

# Code Review

Review code changes against the `base_project` project conventions before they are merged or committed.

## When to Use

- Before committing new code
- Before merging a pull request
- When reviewing a feature branch
- When checking if generated code follows conventions

## Conventions Checklist

### Style & Format

- [ ] Python 3.11+ features used (f-strings, type hints, pattern matching)
- [ ] PEP 8 compliant — Ruff passes (`ruff check .` / `ruff format --check .`)
- [ ] Line length ≤ 100 characters
- [ ] Google-style docstrings on all public classes and functions
- [ ] Full type hints on every function signature and return type
- [ ] `from __future__ import annotations` at top of every file

### Structure

- [ ] All source files under `src/base_project/` — no top-level modules
- [ ] New modules have `__init__.py` with public exports
- [ ] Test files mirror source structure under `tests/`
- [ ] Config values use pydantic-settings — no hardcoded strings or magic numbers

### Naming

- [ ] `snake_case` for functions, variables, modules
- [ ] `PascalCase` for classes
- [ ] `_private_prefix` for private members
- [ ] Descriptive names — no single-letter vars except loop counters

### Configuration

- [ ] New settings added to appropriate pydantic-settings class in `config.py`
- [ ] Corresponding section added to `config/app.toml`
- [ ] Environment variable prefix documented (`APP_` or `DB_`)
- [ ] Default values provided for all settings

### Tests

- [ ] Tests exist under `tests/` mirroring source structure
- [ ] Class-based test organization (like `TestExampleService`)
- [ ] Happy path, edge cases, and error conditions covered
- [ ] Docstrings on all test methods
- [ ] All tests pass (`uv run pytest`)

### Dependencies

- [ ] Runtime deps in `[project] dependencies` of `pyproject.toml`
- [ ] Dev-only deps in `[project.optional-dependencies] dev`
- [ ] No unnecessary packages added

## Review Procedure

1. **Read the diff** — understand what changed and why
2. **Check conventions** — walk through each checklist item above
3. **Run quality gates**:
   ```bash
   uv run ruff check .
   uv run ruff format --check .
   uv run mypy src/
   uv run pytest
   ```
4. **Flag issues** — be specific about what needs to change and why
5. **Approve or request changes** — only approve when all items pass

## Common Issues to Flag

| Issue | Fix |
|-------|-----|
| Missing type hints | Add full type annotations |
| No docstring | Add Google-style docstring with Args/Returns/Raises |
| Hardcoded config | Move to pydantic-settings + TOML |
| Top-level imports | Move into `src/base_project/` |
| Missing tests | Require test coverage for new logic |
| Wrong line length | Wrap at 100 chars |
| Dev dep in main deps | Move to `[project.optional-dependencies] dev` |

# Contributing to Firm Ecosystem

Thank you for your interest in contributing! This guide will help you get started.

## Quick setup

```bash
git clone https://github.com/romainsantoli-web/firm-ecosystem
cd firm-ecosystem

# Install both packages in dev mode
pip install -e "firm-cli[dev]"
pip install -e "mcp-openclaw-extensions[dev]"

# Run all tests
python -m pytest mcp-openclaw-extensions/tests/ firm-cli/tests/ -v
```

## Development workflow

1. **Fork & clone** the repository
2. **Create a branch**: `git checkout -b feat/your-feature`
3. **Make changes** with tests
4. **Run tests**: `python -m pytest -v` — must pass at 100%
5. **Lint**: `ruff check src/ tests/` — zero errors
6. **Commit**: `git commit -m "feat(scope): description"`
7. **Push & open a PR** as draft

## Code standards

### Pydantic on all inputs

Every MCP tool must have a Pydantic `BaseModel` in `src/models.py`:

```python
class MyToolInput(BaseModel):
    config_path: str = Field(
        ...,
        min_length=1,
        max_length=512,
        description="Path to config file"
    )

    @field_validator("config_path")
    @classmethod
    def no_traversal(cls, v: str) -> str:
        if ".." in v:
            raise ValueError("Path traversal blocked")
        return v
```

### Tests

- Every new function/tool: at least **1 positive + 1 negative test**
- Coverage minimum: **80%** (lines + branches)
- Test files: `tests/test_<module>.py`

```bash
python -m pytest tests/ -v --cov=src --cov-fail-under=80
```

### Secrets

- **Never** commit tokens, API keys, or passwords
- Use `mask_secret()` for any display (last 4 chars only)
- `.env` is always in `.gitignore`

### AI-generated content

All AI-generated deliverables must carry:
```
⚠️ AI-generated content — human validation required before use.
```

## Project structure

| Package | Purpose |
|---------|---------|
| `firm-cli/` | CLI entry point (`pip install firm-cli`) |
| `mcp-openclaw-extensions/` | MCP server with 138 tools |
| `skills/` | ClawHub SKILL.md files (34 skills) |
| `souls/` | SOUL.md persona definitions |
| `factory/` | Legacy Bash factory (use `firm init` instead) |

## Good first issues

Look for issues labeled [`good-first-issue`](https://github.com/romainsantoli-web/firm-ecosystem/labels/good-first-issue).

Ideas:
- Add a new sector pack (SKILL.md + factory sector definition)
- Add a new SOUL persona
- Improve test coverage on an existing module
- Fix a documentation typo or broken link

## PR review process

1. PRs trigger CI (lint + test on Python 3.11/3.12/3.13)
2. PRs also trigger the OpenClaw AI reviewer (`openclaw-review.yml`)
3. A human maintainer will review and merge

## Commit convention

```
type(scope): description

Types: feat, fix, docs, test, chore, refactor
Scope: cli, mcp, skills, souls, ci, factory
```

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

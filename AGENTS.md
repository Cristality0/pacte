# Agent Development Guide for Pacte

Quick reference for AI agents and developers working on Pacte. **Read PLAN.md first** for complete implementation details.

---

## 1. Project Overview

**Pacte** is a cross-platform CLI clipboard management tool.

**Key Technologies:** Python 3.13+, uv, typer, textual, pyperclip, pytest, ruff, ty

**Philosophy:** Type safety first, >90% test coverage, clear errors, cross-platform

**Critical Files:**

- `PLAN.md` - Complete implementation plan (READ THIS FIRST)
- `pyproject.toml` - Project config and dependencies
- `src/pacte/` - All application code
- `tests/` - Test files mirroring src structure

---

## 2. Quick Setup

### Development Setup

```bash
# Install dependencies
uv sync

# Verify
uv run pacte --help

# Add dependencies (never edit pyproject.toml manually)
uv add <package>          # Runtime
uv add --dev <package>    # Development
```

### Global Installation

To install pacte globally and use it without `uv run`:

```bash
# Install in development mode (from project directory)
uv pip install -e .

# Or build and install wheel
uv build
uv pip install dist/pacte-*.whl

# Verify global installation
pacte --help
```

### Shell Completions

Enable shell completions for better CLI experience:

```bash
# Bash
echo 'eval "$(pacte --show-completion bash)"' >> ~/.bashrc

# Zsh
echo 'eval "$(pacte --show-completion zsh)"' >> ~/.zshrc

# Fish
echo 'pacte --show-completion fish | source' >> ~/.config/fish/config.fish

# PowerShell (add to $PROFILE)
pacte --show-completion powershell | Out-String | Invoke-Expression
```

---

## 3. Project Architecture

**See PLAN.md sections 3 and 5 for detailed architecture and component specifications.**

**Module Summary:**

- `cli.py` - CLI commands (typer)
- `clipboard.py` - Clipboard operations (pyperclip)
- `file_operations.py` - File I/O, backups (pathlib)
- `history.py` - Operation tracking (json, platformdirs)
- `undo_tui.py` - Interactive TUI (textual)
- `models.py` - Data structures (dataclasses)
- `config.py` - Configuration (tomli)
- `exceptions.py` - Custom exceptions
- `utils.py` - Helper functions

---

## 4. Development Workflow

### Before Starting

1. Read PLAN.md for your task
2. Review existing related code
3. Understand expected behavior from tests

### Code Standards

- **Type hints:** Required on all functions
- **Docstrings:** Required (Google style) on public functions
- **Error handling:** Never let exceptions bubble unhandled
- **Path handling:** Use `pathlib.Path`, never string concatenation
- **Encoding:** Always specify explicitly (`encoding="utf-8"`)

### Import Organization

```python
# Standard library
import json
from pathlib import Path

# Third-party
import typer

# Local
from .exceptions import PacteError
```

### Testing Approach

```bash
# 1. Write test
# 2. Run test (should fail)
uv run pytest tests/test_feature.py -v

# 3. Implement feature
# 4. Run test (should pass)
uv run pytest tests/test_feature.py -v

# 5. Check coverage
uv run pytest --cov=pacte --cov-report=term-missing
```

**Use fixtures:** `tmp_path`, `mock_clipboard`, `history_manager`, `clean_history`

**Test structure:** Arrange → Act → Assert

---

## 5. Essential Commands

```bash
# Testing
uv run pytest                                              # All tests
uv run pytest tests/test_file.py                          # Specific file
uv run pytest tests/test_file.py::test_name               # Specific test
uv run pytest -v -s                                        # With output
uv run pytest --cov=pacte --cov-report=html                # Coverage report

# Quality checks (run before committing)
uv run ruff format .                                       # Format
uv run ruff check . --fix                                  # Lint
uv run ty                                                  # Type check
uv run pytest --cov=pacte --cov-fail-under=90             # Test + coverage

# All at once
uv run ruff format . && uv run ruff check . && uv run ty && uv run pytest --cov=pacte --cov-fail-under=90

# Manual testing
uv run pacte --help
uv run pacte paste test.txt
```

---

## 6. Quality Standards

### Coverage Requirements

- Overall: ≥90%
- Core modules (clipboard, file_operations, history): 100%
- CLI: ≥85%
- TUI: ≥80%

### Type Checking

All code must pass `uv run ty` without errors.

### Docstring Format

```python
def function_name(param1: str, param2: int) -> bool:
    """Short one-line summary.

    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ExceptionType: When this exception is raised
    """
```

---

## 7. Common Tasks

### Adding CLI Command

1. Add `@app.command()` in `cli.py` with type hints
2. Add tests in `tests/test_cli.py`
3. Update `README.md`

### Adding Configuration Option

1. Add field to `Config` dataclass in `models.py`
2. Update `config.py` to load it
3. Document in `pyproject.toml` under `[tool.pacte]`
4. Add tests

### Debugging

```bash
# Show print statements in tests
uv run pytest -v -s

# Debug specific test
uv run pytest tests/test_file.py::test_name -v -s
```

---

## 8. Common Issues

| Issue | Solution |
| ----- | -------- |
| `uv: command not found` | Install uv: `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Import errors in tests | Run `uv sync` |
| Clipboard access fails | Linux: install xclip/xsel; mock in tests |
| Permission denied in tests | Use `tmp_path` fixture |
| Coverage low | Run `uv run pytest --cov=pacte --cov-report=html`, check `htmlcov/index.html` |
| Ruff failures | Run `uv run ruff check . --fix && uv run ruff format .` |
| Type errors | Add missing type hints, fix mismatches |

**Help resources:** PLAN.md, existing tests, [Typer docs](https://typer.tiangolo.com/), [Textual docs](https://textual.textualize.io/), [Pytest docs](https://docs.pytest.org/)

---

## 9. Contribution Checklist

Before submitting code:

- [ ] Type hints on all functions
- [ ] Docstrings on public functions
- [ ] Tests written (unit + integration)
- [ ] `uv run pytest` passes
- [ ] `uv run pytest --cov=pacte --cov-fail-under=90` passes
- [ ] `uv run ruff format .` run
- [ ] `uv run ruff check .` passes
- [ ] `uv run ty` passes
- [ ] README updated (if user-facing)
- [ ] Manual testing performed

### Git Workflow

```bash
git checkout -b feature/new-feature
# Make changes, run quality checks
uv run ruff format . && uv run ruff check . && uv run ty && uv run pytest --cov=pacte --cov-fail-under=90
git add . && git commit -m "Add feature X"
git push origin feature/new-feature
```

### Commit Format

```text
First line: Imperative mood, <50 chars

- Bullet points explaining changes
- Focus on what and why
```

---

## 10. Quick Reference

### File Locations

- Source: `src/pacte/`
- Tests: `tests/`
- Config: `pyproject.toml`
- History: `~/.config/pacte/history.json`
- Coverage: `htmlcov/index.html`

### Key Patterns

```python
# Error handling
try:
    result = operation()
except SpecificError as e:
    raise CustomError(f"Context: {e}") from e

# Path handling
path = Path("file.txt")  # Good
path = "file.txt"        # Bad

# Test structure
def test_feature(tmp_path, mock_clipboard):
    # Arrange
    # Act
    # Assert
```

### Project-Specific Details

**See PLAN.md sections 7, 8, and Appendices for:**

- History file format
- Backup file naming convention
- Configuration priority
- Exit codes
- Error messages

---

## 11. Agent Workflow

**For AI Coding Assistants:**

1. Read PLAN.md section for current task
2. Read existing related code
3. Write test(s) for new feature
4. Implement feature to pass tests
5. Run: `uv run pytest <test-file>`
6. Run: `uv run ruff format . && uv run ruff check .`
7. Run: `uv run ty`
8. Verify manually if needed
9. Move to next task

**Common Mistakes to Avoid:**

- ❌ Not reading PLAN.md first
- ❌ Missing type hints or docstrings
- ❌ Skipping tests
- ❌ Not using `tmp_path` fixture
- ❌ Using string paths instead of `pathlib.Path`
- ❌ Hardcoding paths instead of using `platformdirs`
- ❌ Not handling errors properly

**Implementation Order:** Follow PLAN.md Phase 1 → 2 → 3 → 4 → 5

---

## 12. External Resources

- [uv](https://github.com/astral-sh/uv) - Package manager
- [Typer](https://typer.tiangolo.com/) - CLI framework
- [Textual](https://textual.textualize.io/) - TUI framework
- [Pytest](https://docs.pytest.org/) - Testing
- [Ruff](https://docs.astral.sh/ruff/) - Linting/formatting

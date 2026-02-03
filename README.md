# Pacte

**Pacte** is a cross-platform CLI clipboard management tool that makes working with clipboard content and files seamless.

## Features

- ✨ **Paste clipboard to files** with automatic backups
- ➕ **Append clipboard content** to existing files
- 📋 **Copy file contents** to clipboard
- ↩️ **Undo operations** with interactive TUI
- 🎯 **Operation history** tracking (last 50 operations)
- 🔒 **Automatic backups** before overwriting files
- ⚙️ **Configurable** via `pyproject.toml`
- 🚀 **Fast** and lightweight
- 💻 **Cross-platform** (Windows, macOS, Linux)

## Installation

### Development Install

```bash
# Using uv (recommended)
git clone <repository>
cd pacte
uv sync

# Run directly
uv run pacte --help
```

### Global Install

Install pacte globally to use it anywhere without `uv run`:

```bash
# From the project directory
uv pip install -e .

# Or install from wheel
uv build
uv pip install dist/pacte-*.whl
```

After global installation, you can use `pacte` directly:

```bash
pacte --help
pacte paste output.txt
```

### Shell Completions

Pacte supports shell completions for bash, zsh, fish, and PowerShell (provided by Typer).

#### Bash

```bash
# Generate completion script
pacte --show-completion bash > ~/.local/share/bash-completion/completions/pacte

# Or add to your ~/.bashrc:
echo 'eval "$(pacte --show-completion bash)"' >> ~/.bashrc
source ~/.bashrc
```

#### Zsh

```bash
# Generate completion script
pacte --show-completion zsh > ~/.zsh/completions/_pacte

# Make sure completions directory is in your fpath (add to ~/.zshrc if needed):
echo 'fpath=(~/.zsh/completions $fpath)' >> ~/.zshrc
echo 'autoload -Uz compinit && compinit' >> ~/.zshrc
source ~/.zshrc
```

#### Fish

```bash
# Generate completion script
pacte --show-completion fish > ~/.config/fish/completions/pacte.fish

# Reload completions
source ~/.config/fish/completions/pacte.fish
```

#### PowerShell

```powershell
# Add to your PowerShell profile
pacte --show-completion powershell | Out-String | Invoke-Expression

# To make it permanent, add to your profile:
# Find profile location: $PROFILE
# Add this line to the profile:
pacte --show-completion powershell | Out-String | Invoke-Expression
```

#### Installing Completions Script

For a more permanent setup, add the completion generation to your shell's startup file:

**Bash** (`~/.bashrc`):
```bash
eval "$(pacte --show-completion bash)"
```

**Zsh** (`~/.zshrc`):
```bash
eval "$(pacte --show-completion zsh)"
```

**Fish** (`~/.config/fish/config.fish`):
```fish
pacte --show-completion fish | source
```

## Quick Start

```bash
# Paste clipboard to file
pacte paste output.txt

# Append clipboard to file
pacte append log.txt

# Copy file to clipboard
pacte copy input.txt

# Undo last operation
pacte undo --last

# Interactive undo (TUI)
pacte undo
```

## Usage

### Paste Command

Paste clipboard content to a file (overwrites if exists):

```bash
# Basic paste
pacte paste output.txt

# Skip backup
pacte paste output.txt --no-backup

# Force overwrite without confirmation
pacte paste output.txt --force
```

### Append Command

Append clipboard content to a file:

```bash
# Append with newline
pacte append log.txt

# Append without newline
pacte append log.txt --no-newline

# Skip backup
pacte append log.txt --no-backup
```

### Copy Command

Copy file content to clipboard:

```bash
# Copy with default encoding (UTF-8)
pacte copy input.txt

# Specify encoding
pacte copy input.txt --encoding latin1
```

### Undo Command

Undo paste/append operations:

```bash
# Interactive TUI selection
pacte undo

# Undo last operation immediately
pacte undo --last

# List operation history
pacte undo --list
```

## Configuration

Configure Pacte by adding a `[tool.pacte]` section to your `pyproject.toml`:

```toml
[tool.pacte]
max_history = 50              # Maximum operations to keep
default_encoding = "utf-8"    # Default file encoding
backup_on_paste = true        # Create backup on paste
backup_on_append = true       # Create backup on append
preview_length = 50           # Preview length in history

[tool.pacte.undo_tui]
datetime_format = "%H:%M:%S"  # Time format in TUI
```

## How It Works

### Operation Flow

1. **Paste/Append**: Creates backup → Writes content → Records in history
2. **Undo**: Restores from backup (or deletes if new file) → Removes from history

### History Storage

- Location: `~/.config/pacte/history.json` (platform-specific)
- Format: JSON with operation metadata
- Automatic cleanup when limit exceeded
- Backup files cleaned up with old operations

### Backup Files

- Format: `{filename}.{timestamp}.bak`
- Example: `output.txt.20240202_153045.123456.bak`
- Automatically deleted after successful undo

## Development

### Setup

```bash
# Install dependencies
uv sync

# Install dev dependencies
uv add --dev pytest pytest-cov pytest-mock pytest-asyncio

# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=pacte --cov-report=html

# Type checking
uv run ty

# Linting and formatting
uv run ruff check .
uv run ruff format .
```

### Running Tests

```bash
# All tests
uv run pytest -v

# Specific test file
uv run pytest tests/test_clipboard.py -v

# With coverage report
uv run pytest --cov=pacte --cov-report=term-missing
```

### Project Structure

```text
pacte/
├── src/pacte/
│   ├── __init__.py              # Package entry
│   ├── cli.py                   # CLI commands
│   ├── clipboard.py             # Clipboard operations
│   ├── file_operations.py       # File I/O and backups
│   ├── history.py               # History management
│   ├── undo_tui.py              # Interactive TUI
│   ├── models.py                # Data models
│   ├── config.py                # Configuration
│   ├── exceptions.py            # Custom exceptions
│   └── utils.py                 # Utilities
├── tests/
│   ├── conftest.py              # Test fixtures
│   ├── test_*.py                # Test files
│   └── ...
├── pyproject.toml               # Project config
└── README.md                    # This file
```

## Examples

### Basic Workflow

```bash
# Copy some text to clipboard
echo "Hello, World!" | clip  # or pbcopy on macOS

# Paste to file
pacte output.txt
# ✓ Pasted clipboard content to 'output.txt' (13 bytes)

# Append more content
echo "More content" | clip
pacte append output.txt
# ✓ Backed up to 'output.txt.20240202_153045.bak'
# ✓ Appended clipboard content to 'output.txt' (26 bytes)

# Undo last operation
pacte undo --last
# ✓ Restored 'output.txt' from backup
# ✓ Operation removed from history
```

### Working with Files

```bash
# Copy file to clipboard
pacte copy config.json
# ✓ Copied 'config.json' to clipboard (1.2 KB)

# Paste to new file
pacte backup-config.json
# ✓ Pasted clipboard content to 'backup-config.json' (1.2 KB)
```

### History Management

```bash
# View operation history
pacte undo --list
# Operation History:
# 1. [paste] output.txt - Hello, World!
# 2. [append] output.txt - More content
# 3. [paste] backup-config.json - {"key": "value"...

# Interactive undo with TUI
pacte undo
# (Opens interactive selection interface)
```

## Error Handling

Pacte provides clear error messages with exit codes:

- `0`: Success
- `1`: General error
- `2`: Clipboard error (empty or inaccessible)
- `3`: File operation error
- `4`: History error
- `5`: User cancelled operation

## Requirements

- Python 3.13+
- `uv` package manager
- Dependencies:
  - typer
  - pyperclip
  - textual
  - platformdirs
  - rich

## License

[Add your license here]

## Contributing

Contributions are welcome! Please ensure:

1. All tests pass (`uv run pytest`)
2. Code is formatted (`uv run ruff format .`)
3. No linting errors (`uv run ruff check .`)
4. Type checking passes (`uv run ty`)
5. Coverage remains >90%

## Acknowledgments

Built with:

- [Typer](https://typer.tiangolo.com/) - CLI framework
- [Textual](https://textual.textualize.io/) - TUI framework  
- [pyperclip](https://github.com/asweigart/pyperclip) - Clipboard access
- [uv](https://github.com/astral-sh/uv) - Fast Python package manager

# Pacte - Clipboard Paste Application

## Implementation Plan

---

## 1. Overview

**Pacte** is a cross-platform CLI clipboard management tool that enables users to:

- Paste clipboard content to files
- Append clipboard content to existing files
- Copy file content to clipboard
- Undo paste/append operations with interactive TUI selection
- Maintain operation history with automatic backup management

**Technology Stack:** Python 3.13+, uv, typer, textual, pyperclip, pytest, ruff, ty

**Non-Functional Requirements:**

- Cross-platform: Windows, macOS, Linux
- Performance: <100ms for paste operations
- Reliability: 100% backup success before operations
- Maintainability: >90% test coverage, full type hints

---

## 2. Core Features

### 2.1 Paste to File

```bash
pacte output.txt
pacte output.txt --no-backup
pacte output.txt --force
```

- Get clipboard content
- Create backup if file exists
- Write clipboard to file
- Record in history

### 2.2 Append to File

```bash
pacte append output.txt
pacte append output.txt --no-newline
```

- Get clipboard content
- Create backup if file exists
- Append clipboard to file
- Record in history

### 2.3 Copy File to Clipboard

```bash
pacte copy input.txt
pacte copy input.txt --encoding latin1
```

- Read file content
- Copy to system clipboard
- Handle encoding (default UTF-8)
- Detect binary files with warning

### 2.4 Undo Operations

```bash
pacte undo              # Interactive TUI
pacte undo --last       # Undo last without prompt
pacte undo --list       # Show history
```

- Interactive TUI using Textual
- Display last 50 operations (timestamp, type, file, preview)
- Restore from backup or delete if new file
- Remove from history after undo

---

## 3. Architecture

### 3.1 System Architecture

```
┌─────────────────────────────────────────────────────┐
│                   CLI Layer (Typer)                 │
│  Commands: paste, append, copy, undo                │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────┴──────────────────────────────────┐
│              Application Logic Layer                │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────┐  │
│  │  Clipboard  │  │ File Ops     │  │  History   │  │
│  │  Manager    │  │ Manager      │  │  Manager   │  │
│  └─────────────┘  └──────────────┘  └────────────┘  │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────┴──────────────────────────────────┐
│              External Dependencies                  │
│  pyperclip | pathlib | platformdirs | json          │
└─────────────────────────────────────────────────────┘
```

### 3.2 Data Flow

**Paste Operation:**

1. CLI validates arguments
2. Check file exists → Create backup
3. Get clipboard → Validate not empty
4. Write to file
5. Record in history
6. Display success

**Undo Operation:**

1. Load history from ~/.config/pacte/history.json
2. Launch TUI with operations
3. User selects operation
4. Restore from backup or delete file
5. Remove from history
6. Display success

### 3.3 Design Decisions

| Decision | Rationale |
|----------|-----------|
| Textual for TUI | Modern, well-maintained, rich features |
| History limit: 50 | Balance storage/performance and usefulness |
| Backup strategy | More reliable than storing content in history |
| JSON history | Human-readable, easy to debug |
| platformdirs | Cross-platform standard config directories |
| Typer for CLI | Type-safe, auto help generation |

---

## 4. Project Structure

```
pacte/
├── src/pacte/
│   ├── __init__.py              # Package entry, expose main()
│   ├── cli.py                   # CLI commands
│   ├── clipboard.py             # Clipboard operations
│   ├── file_operations.py       # File I/O, backups
│   ├── history.py               # History tracking
│   ├── undo_tui.py              # Interactive TUI
│   ├── models.py                # Data models
│   ├── config.py                # Configuration
│   ├── exceptions.py            # Custom exceptions
│   └── utils.py                 # Utilities
├── tests/
│   ├── conftest.py              # Fixtures
│   ├── test_clipboard.py
│   ├── test_file_operations.py
│   ├── test_history.py
│   ├── test_cli.py
│   ├── test_undo_tui.py
│   └── test_integration.py
├── pyproject.toml
├── README.md
├── PLAN.md
├── AGENTS.md
├── .gitignore
├── .python-version
└── uv.lock
```

---

## 5. Core Components

### 5.1 Data Models (models.py)

**Operation:** Tracks paste/append operations

- `id` (UUID), `timestamp`, `operation_type` (paste/append)
- `target_path`, `backup_path` (None if new file), `content_preview`

**Config:** Application configuration

- `max_history` (50), `default_encoding` (utf-8)
- `backup_on_paste/append` (true), `preview_length` (50)

### 5.2 Module Responsibilities

| Module | Purpose | Key Functions |
|--------|---------|---------------|
| clipboard.py | Clipboard access | get_clipboard_content, set_clipboard_content |
| file_operations.py | File I/O | create_backup, write_to_file, read_from_file, restore_from_backup |
| history.py | History management | HistoryManager class with add/get/remove/cleanup |
| undo_tui.py | Interactive TUI | UndoSelectionApp, select_operation_to_undo |
| cli.py | CLI interface | paste, append, copy, undo commands |
| config.py | Configuration | load_config, get_default_config |
| exceptions.py | Error handling | PacteError, ClipboardError, FileOperationError, HistoryError |

### 5.3 Exception Hierarchy

- `PacteError` (base)
  - `ClipboardError`
    - `EmptyClipboardError`
  - `FileOperationError`
  - `HistoryError`
  - `ConfigError`

---

## 6. CLI Reference

### Commands

```bash
# Paste
pacte output.txt [--no-backup] [--force]

# Append
pacte append output.txt [--no-newline] [--no-backup]

# Copy
pacte copy input.txt [--encoding ENCODING]

# Undo
pacte undo [--last] [--list]
```

### Exit Codes

- 0: Success
- 1: General error
- 2: Clipboard error
- 3: File operation error
- 4: History error
- 5: User cancelled

---

## 7. History & Undo System

### 7.1 Storage

**Location:** `~/.config/pacte/history.json` (platform-specific via platformdirs)

**Format:**

```json
{
  "operations": [
    {
      "id": "uuid",
      "timestamp": "ISO format",
      "operation_type": "paste|append",
      "target_path": "absolute path",
      "backup_path": "absolute path or null",
      "content_preview": "first 50 chars"
    }
  ],
  "version": "1.0"
}
```

### 7.2 Behavior

**Limits:**

- Max 50 operations (configurable)
- Oldest removed when limit reached
- Backup files cleaned up with old operations

**Undo Actions:**

| Scenario | Action |
|----------|--------|
| File overwritten | Restore from backup, delete backup |
| File appended | Restore from backup, delete backup |
| File newly created | Delete file |
| Backup missing | Error, don't modify history |

### 7.3 TUI Layout

```
┌─────────────────────────────────────────────────────────────┐
│ Pacte - Undo Operation                                      │
├─────────────────────────────────────────────────────────────┤
│  #  Time       Type    File              Preview            │
├─────────────────────────────────────────────────────────────┤
│  1  15:30:45  paste   output.txt         Hello, this is...  │
│  2  15:25:12  append  log.txt            New log entry...   │
│  3  15:20:03  paste   data.json          {"key": "value"... │
├─────────────────────────────────────────────────────────────┤
│ ↑↓ Navigate | Enter Select | Esc Cancel | q Quit            │
└─────────────────────────────────────────────────────────────┘
```

---

## 8. Configuration

### 8.1 Settings (pyproject.toml)

```toml
[tool.pacte]
max_history = 50
default_encoding = "utf-8"
backup_on_paste = true
backup_on_append = true
preview_length = 50

[tool.pacte.undo_tui]
theme = "dark"
datetime_format = "%H:%M:%S"
```

### 8.2 Priority Order

1. Command-line flags (highest)
2. `[tool.pacte]` in pyproject.toml
3. Default values (lowest)

---

## 9. Testing Strategy

### 9.1 Coverage Goals

- Overall: >90%
- Core modules (clipboard, file_operations, history): 100%
- CLI: >85%
- TUI: >80%

### 9.2 Test Structure

**Fixtures (conftest.py):**

- `tmp_path`: Temporary directory
- `mock_clipboard`: Mocked pyperclip
- `history_manager`: Pre-configured manager
- `clean_history`: Clean state

**Test Categories:**

- Unit tests: Individual module functions
- Integration tests: CLI commands, TUI interaction
- End-to-end tests: Complete workflows

---

## 10. Dependencies

### 10.1 Runtime

```bash
uv add typer "typer[all]" pyperclip textual platformdirs
```

Expected versions:

- typer[all] >= 0.9.0
- pyperclip >= 1.8.2
- textual >= 0.47.0
- platformdirs >= 4.1.0

### 10.2 Development

```bash
uv add --dev pytest pytest-cov pytest-mock pytest-asyncio
```

Expected versions:

- pytest >= 7.4.0
- pytest-cov >= 4.1.0
- pytest-mock >= 3.12.0
- pytest-asyncio >= 0.23.0 (for textual tests)
- ruff >= 0.14.14
- ty >= 0.0.14

---

## 11. Implementation Phases

### Phase 1: Foundation (~30 min)

1. **Dependencies:** Install runtime and dev dependencies
2. **Data Models:** Create Operation and Config dataclasses
3. **Exceptions:** Define exception hierarchy
4. **Configuration:** Implement config loading from pyproject.toml
5. **Utilities:** Helper functions (timestamps, etc.)

### Phase 2: Core Functionality (~1 hour)

6. **Clipboard:** Get/set operations with error handling
2. **File Operations:** Write, append, backup, restore functions
3. **History:** HistoryManager class with persistence and cleanup
4. **Tests:** Comprehensive unit tests for all core modules

### Phase 3: CLI & TUI (~1 hour)

10. **CLI:** Implement all typer commands with proper error handling
2. **TUI:** Build Textual app for interactive undo selection
3. **Integration:** Wire everything together
4. **Tests:** CLI command tests and TUI interaction tests

### Phase 4: Integration & Polish (~45 min)

14. **Entry Point:** Configure **init**.py properly
2. **Integration Tests:** End-to-end workflows
3. **Documentation:** Complete README with examples
4. **Quality:** Run full test suite, type checking, linting

### Phase 5: Final Checks (~15 min)

18. **Verification Checklist:**
    - [ ] All tests pass
    - [ ] Coverage >90%
    - [ ] No ruff violations
    - [ ] No ty type errors
    - [ ] CLI help messages clear
    - [ ] README accurate
    - [ ] Manual smoke testing

**Total Estimated Time:** ~3.5 hours

---

## 12. Success Criteria

### Must Have (v1.0)

- ✅ All four commands work: paste, append, copy, undo
- ✅ Cross-platform clipboard access
- ✅ File backup before operations
- ✅ Interactive TUI for undo with history
- ✅ >90% test coverage
- ✅ Clean type checking (ty passes)
- ✅ No linting errors (ruff passes)
- ✅ Configuration in pyproject.toml
- ✅ Clear README with examples

### Nice to Have

- 🎯 HTML coverage report
- 🎯 CI/CD pipeline setup
- 🎯 Performance benchmarks
- 🎯 Video demo/GIF in README

---

## 13. Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Clipboard access fails on platforms | High | Comprehensive error handling, fallback messages |
| Backup file collision | Medium | Timestamp includes microseconds |
| Large file performance | Low | Add file size warnings, test with large files |
| History file corruption | Medium | JSON validation, backup history file |
| TUI rendering issues | Low | Test in multiple terminals, fallback to list mode |

---

## 14. Future Enhancements (Out of Scope for v1)

**Potential Features:**

- Multi-clipboard support with named slots
- Clipboard history (not just paste operations)
- Templates with variable substitution
- Remote sync across devices
- Binary file support (images, PDFs)
- Compression for large content
- Encryption for sensitive content
- Plugin system
- Watch mode (auto-paste on clipboard change)
- Optional GUI

**Performance Optimizations:**

- Lazy load history
- Async file operations for large files
- Streaming for very large content
- Batch backup cleanup

**Platform-Specific:**

- Windows: Native clipboard format support
- macOS: Pasteboard type detection
- Linux: Multiple clipboard selection (primary, clipboard)

---

## Appendix A: File Naming Conventions

### Backup Files

- Format: `{original_name}.{timestamp}.bak`
- Example: `output.txt.20240202_153045.123456.bak`

### History File

- Windows: `C:\Users\{user}\AppData\Local\pacte\pacte\history.json`
- macOS: `~/Library/Application Support/pacte/history.json`
- Linux: `~/.config/pacte/history.json`

---

## Appendix B: User Experience Guidelines

### Error Messages

- Clear, actionable error descriptions
- Include context (file paths, operation type)
- Suggest solutions when possible

### Success Messages

- Confirm action taken
- Show relevant details (file size, backup location)
- Use visual indicators (✓ checkmarks)

### Examples

```
Error: Clipboard is empty
  Cannot paste empty clipboard content to file.

✓ Pasted clipboard content to 'output.txt' (42 bytes)

✓ Backed up to 'output.txt.20240202_153045.bak'
✓ Pasted clipboard content to 'output.txt' (156 bytes)

✓ Restored 'output.txt' from backup
✓ Operation removed from history
```

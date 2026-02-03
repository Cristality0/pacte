"""Pytest fixtures and configuration."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from pacte.history import HistoryManager


@pytest.fixture
def mock_clipboard(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Mock clipboard operations."""
    mock = MagicMock()
    mock.paste.return_value = "test clipboard content"
    mock.copy.return_value = None

    monkeypatch.setattr("pacte.clipboard.pyperclip", mock)
    return mock


@pytest.fixture
def history_manager(tmp_path: Path) -> HistoryManager:
    """Create a HistoryManager with temporary storage."""
    return HistoryManager(history_dir=tmp_path, max_history=50)


@pytest.fixture
def clean_history(history_manager: HistoryManager) -> HistoryManager:
    """Provide a clean history manager (removes history file if exists)."""
    if history_manager.history_file.exists():
        history_manager.history_file.unlink()
    return history_manager

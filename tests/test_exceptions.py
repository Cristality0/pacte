"""Tests for exception hierarchy."""

from pacte.exceptions import (
    ClipboardError,
    ConfigError,
    EmptyClipboardError,
    FileOperationError,
    HistoryError,
    PacteError,
)


def test_base_exception() -> None:
    """Test base PacteError exception."""
    error = PacteError("test error")
    assert str(error) == "test error"
    assert isinstance(error, Exception)


def test_clipboard_error() -> None:
    """Test ClipboardError exception."""
    error = ClipboardError("clipboard error")
    assert isinstance(error, PacteError)
    assert str(error) == "clipboard error"


def test_empty_clipboard_error() -> None:
    """Test EmptyClipboardError exception."""
    error = EmptyClipboardError("empty")
    assert isinstance(error, ClipboardError)
    assert isinstance(error, PacteError)


def test_file_operation_error() -> None:
    """Test FileOperationError exception."""
    error = FileOperationError("file error")
    assert isinstance(error, PacteError)


def test_history_error() -> None:
    """Test HistoryError exception."""
    error = HistoryError("history error")
    assert isinstance(error, PacteError)


def test_config_error() -> None:
    """Test ConfigError exception."""
    error = ConfigError("config error")
    assert isinstance(error, PacteError)

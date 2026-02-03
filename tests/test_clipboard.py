"""Tests for clipboard operations."""

from unittest.mock import MagicMock

import pytest

from pacte.clipboard import get_clipboard_content, set_clipboard_content
from pacte.exceptions import ClipboardError, EmptyClipboardError


def test_get_clipboard_content_success(mock_clipboard: MagicMock) -> None:
    """Test getting clipboard content successfully."""
    mock_clipboard.paste.return_value = "test content"

    content = get_clipboard_content()

    assert content == "test content"
    mock_clipboard.paste.assert_called_once()


def test_get_clipboard_content_empty(mock_clipboard: MagicMock) -> None:
    """Test getting clipboard content when empty."""
    mock_clipboard.paste.return_value = ""

    with pytest.raises(EmptyClipboardError, match="Clipboard is empty"):
        get_clipboard_content()


def test_get_clipboard_content_none(mock_clipboard: MagicMock) -> None:
    """Test getting clipboard content when None."""
    mock_clipboard.paste.return_value = None

    with pytest.raises(EmptyClipboardError, match="Clipboard is empty"):
        get_clipboard_content()


def test_get_clipboard_content_error(mock_clipboard: MagicMock) -> None:
    """Test getting clipboard content with error."""
    mock_clipboard.paste.side_effect = RuntimeError("Clipboard error")

    with pytest.raises(ClipboardError, match="Failed to access clipboard"):
        get_clipboard_content()


def test_set_clipboard_content_success(mock_clipboard: MagicMock) -> None:
    """Test setting clipboard content successfully."""
    set_clipboard_content("test content")

    mock_clipboard.copy.assert_called_once_with("test content")


def test_set_clipboard_content_error(mock_clipboard: MagicMock) -> None:
    """Test setting clipboard content with error."""
    mock_clipboard.copy.side_effect = RuntimeError("Clipboard error")

    with pytest.raises(ClipboardError, match="Failed to set clipboard content"):
        set_clipboard_content("test content")

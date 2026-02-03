"""Clipboard operations for Pacte."""

import pyperclip

from .exceptions import ClipboardError, EmptyClipboardError


def get_clipboard_content() -> str:
    """Get content from system clipboard.

    Returns:
        Clipboard content as string

    Raises:
        ClipboardError: If clipboard access fails
        EmptyClipboardError: If clipboard is empty
    """
    try:
        content = pyperclip.paste()
        # pyperclip.paste() can return None on some platforms when clipboard is empty
        if content is None or not content:
            raise EmptyClipboardError("Clipboard is empty")
        return content
    except EmptyClipboardError:
        raise
    except Exception as e:
        raise ClipboardError(f"Failed to access clipboard: {e}") from e


def set_clipboard_content(content: str) -> None:
    """Set content to system clipboard.

    Args:
        content: Content to copy to clipboard

    Raises:
        ClipboardError: If clipboard access fails
    """
    try:
        pyperclip.copy(content)
    except Exception as e:
        raise ClipboardError(f"Failed to set clipboard content: {e}") from e

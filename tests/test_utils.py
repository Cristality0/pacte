"""Tests for utility functions."""

from datetime import datetime

from pacte.utils import (
    format_file_size,
    get_backup_timestamp,
    get_timestamp,
    truncate_preview,
)


def test_get_timestamp() -> None:
    """Test getting ISO format timestamp."""
    timestamp = get_timestamp()

    # Should be a valid ISO format timestamp
    datetime.fromisoformat(timestamp)
    assert "T" in timestamp


def test_get_backup_timestamp() -> None:
    """Test getting backup timestamp."""
    timestamp = get_backup_timestamp()

    # Should have format: YYYYMMDD_HHMMSS.ffffff
    parts = timestamp.split("_")
    assert len(parts) == 2
    assert len(parts[0]) == 8  # YYYYMMDD
    assert "." in parts[1]  # HHMMSS.ffffff


def test_truncate_preview_short() -> None:
    """Test truncating preview with short content."""
    content = "Hello, World!"
    preview = truncate_preview(content, max_length=50)

    assert preview == "Hello, World!"


def test_truncate_preview_long() -> None:
    """Test truncating preview with long content."""
    content = "A" * 100
    preview = truncate_preview(content, max_length=50)

    assert len(preview) == 53  # 50 + "..."
    assert preview.endswith("...")
    assert preview.startswith("A" * 50)


def test_truncate_preview_exact() -> None:
    """Test truncating preview with exact length."""
    content = "A" * 50
    preview = truncate_preview(content, max_length=50)

    assert preview == content


def test_format_file_size_bytes() -> None:
    """Test formatting file size in bytes."""
    assert format_file_size(42) == "42 bytes"
    assert format_file_size(1023) == "1023 bytes"


def test_format_file_size_kb() -> None:
    """Test formatting file size in KiB."""
    assert format_file_size(1024) == "1.0 KiB"
    assert format_file_size(2048) == "2.0 KiB"
    assert format_file_size(1536) == "1.5 KiB"


def test_format_file_size_mb() -> None:
    """Test formatting file size in MiB."""
    assert format_file_size(1024 * 1024) == "1.0 MiB"
    assert format_file_size(1024 * 1024 * 2) == "2.0 MiB"
    assert format_file_size(1024 * 1024 + 512 * 1024) == "1.5 MiB"

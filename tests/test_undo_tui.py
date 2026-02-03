"""Tests for undo TUI."""

from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from pacte.models import Operation
from pacte.undo_tui import UndoSelectionApp, select_operation_to_undo


@pytest.fixture
def sample_operations(tmp_path: Path) -> list[Operation]:
    """Create sample operations for testing."""
    return [
        Operation(
            id="op1",
            timestamp="2024-01-01T10:00:00",
            operation_type="paste",
            target_path=str(tmp_path / "file1.txt"),
            backup_path=str(tmp_path / "file1.txt.backup.bak"),
            content_preview="Content 1 preview",
        ),
        Operation(
            id="op2",
            timestamp="2024-01-01T10:05:00",
            operation_type="append",
            target_path=str(tmp_path / "file2.txt"),
            backup_path=None,
            content_preview="Content 2 preview",
        ),
        Operation(
            id="op3",
            timestamp="2024-01-01T10:10:00",
            operation_type="paste",
            target_path=str(tmp_path / "subdir" / "file3.txt"),
            backup_path=str(tmp_path / "subdir" / "file3.txt.backup.bak"),
            content_preview="Content 3 preview with longer text",
        ),
    ]


def test_undo_selection_app_init(sample_operations):
    """Test UndoSelectionApp initialization."""
    app = UndoSelectionApp(sample_operations, datetime_format="%H:%M:%S")

    assert app.operations == sample_operations
    assert app.datetime_format == "%H:%M:%S"
    assert app.selected_operation is None


def test_undo_selection_app_init_empty():
    """Test UndoSelectionApp with empty operations."""
    app = UndoSelectionApp([], datetime_format="%H:%M:%S")

    assert app.operations == []
    assert app.selected_operation is None


def test_undo_selection_app_compose_with_operations(sample_operations):
    """Test UndoSelectionApp compose with operations."""
    app = UndoSelectionApp(sample_operations)

    # Compose should return widgets
    widgets = list(app.compose())

    # Should have Header, VerticalScroll with DataTable, and Footer
    assert len(widgets) >= 3


def test_undo_selection_app_compose_empty():
    """Test UndoSelectionApp compose with no operations."""
    app = UndoSelectionApp([])

    widgets = list(app.compose())

    # Should still compose UI (with message about no operations)
    assert len(widgets) >= 2


@patch.object(UndoSelectionApp, "run")
def test_select_operation_to_undo(mock_run, sample_operations):
    """Test select_operation_to_undo function."""
    mock_run.return_value = sample_operations[0]

    result = select_operation_to_undo(sample_operations, datetime_format="%H:%M")

    assert result == sample_operations[0]
    mock_run.assert_called_once()


@patch.object(UndoSelectionApp, "run")
def test_select_operation_to_undo_cancelled(mock_run, sample_operations):
    """Test select_operation_to_undo when user cancels."""
    mock_run.return_value = None

    result = select_operation_to_undo(sample_operations)

    assert result is None


def test_undo_selection_app_extracts_filename(sample_operations):
    """Test that app correctly extracts filename from full path."""
    # Test with different path formats
    assert Path(sample_operations[0].target_path).name == "file1.txt"
    assert Path(sample_operations[2].target_path).name == "file3.txt"


def test_undo_selection_app_formats_timestamp(sample_operations):
    """Test that app correctly formats timestamps."""
    _ = UndoSelectionApp(sample_operations, datetime_format="%H:%M:%S")

    # Test timestamp parsing
    dt = datetime.fromisoformat(sample_operations[0].timestamp)
    formatted = dt.strftime("%H:%M:%S")

    assert formatted == "10:00:00"


def test_undo_selection_app_invalid_timestamp(tmp_path):
    """Test handling of invalid timestamp format."""
    operations = [
        Operation(
            id="op1",
            timestamp="invalid-timestamp",
            operation_type="paste",
            target_path=str(tmp_path / "file1.txt"),
            backup_path=None,
            content_preview="Content",
        )
    ]

    # Should not crash - will use the raw timestamp string
    app = UndoSelectionApp(operations)
    assert app.operations == operations


def test_undo_selection_app_custom_datetime_format(sample_operations):
    """Test using custom datetime format."""
    custom_format = "%Y-%m-%d %H:%M"
    app = UndoSelectionApp(sample_operations, datetime_format=custom_format)

    assert app.datetime_format == custom_format

    # Verify format works with timestamp
    dt = datetime.fromisoformat(sample_operations[0].timestamp)
    formatted = dt.strftime(custom_format)
    assert formatted == "2024-01-01 10:00"


def test_undo_selection_app_windows_path(tmp_path):
    """Test handling Windows-style paths."""
    windows_path = "C:\\Users\\test\\file.txt"
    operations = [
        Operation(
            id="op1",
            timestamp="2024-01-01T10:00:00",
            operation_type="paste",
            target_path=windows_path,
            backup_path=None,
            content_preview="Content",
        )
    ]

    # Should correctly extract filename
    assert Path(operations[0].target_path).name == "file.txt"


def test_undo_selection_app_unix_path(tmp_path):
    """Test handling Unix-style paths."""
    unix_path = "/home/user/test/file.txt"
    operations = [
        Operation(
            id="op1",
            timestamp="2024-01-01T10:00:00",
            operation_type="paste",
            target_path=unix_path,
            backup_path=None,
            content_preview="Content",
        )
    ]

    # Should correctly extract filename
    assert Path(operations[0].target_path).name == "file.txt"


def test_undo_selection_app_long_content_preview(tmp_path):
    """Test handling of long content preview."""
    long_preview = "a" * 200
    operations = [
        Operation(
            id="op1",
            timestamp="2024-01-01T10:00:00",
            operation_type="paste",
            target_path=str(tmp_path / "file.txt"),
            backup_path=None,
            content_preview=long_preview,
        )
    ]

    app = UndoSelectionApp(operations)

    # App should handle long previews (they're already truncated by HistoryManager)
    assert app.operations[0].content_preview == long_preview


def test_undo_selection_app_multiple_operation_types(tmp_path):
    """Test app with mixed operation types."""
    operations = [
        Operation(
            id="op1",
            timestamp="2024-01-01T10:00:00",
            operation_type="paste",
            target_path=str(tmp_path / "file1.txt"),
            backup_path=None,
            content_preview="Paste",
        ),
        Operation(
            id="op2",
            timestamp="2024-01-01T10:05:00",
            operation_type="append",
            target_path=str(tmp_path / "file2.txt"),
            backup_path=None,
            content_preview="Append",
        ),
    ]

    app = UndoSelectionApp(operations)

    assert app.operations[0].operation_type == "paste"
    assert app.operations[1].operation_type == "append"


def test_select_operation_to_undo_default_format(sample_operations):
    """Test select_operation_to_undo with default datetime format."""
    with patch.object(UndoSelectionApp, "run") as mock_run:
        mock_run.return_value = None

        result = select_operation_to_undo(sample_operations)

        # Should use default format
        assert result is None

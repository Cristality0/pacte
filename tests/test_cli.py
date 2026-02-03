"""Tests for CLI commands."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from pacte.cli import app

runner = CliRunner()


def test_cli_help() -> None:
    """Test CLI help command."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Cross-platform CLI clipboard management tool" in result.stdout


def test_paste_command_help() -> None:
    """Test paste command help."""
    result = runner.invoke(app, ["paste", "--help"])
    assert result.exit_code == 0
    assert "Paste clipboard content to a file" in result.stdout


def test_append_command_help() -> None:
    """Test append command help."""
    result = runner.invoke(app, ["append", "--help"])
    assert result.exit_code == 0
    assert "Append clipboard content to a file" in result.stdout


def test_copy_command_help() -> None:
    """Test copy command help."""
    result = runner.invoke(app, ["copy", "--help"])
    assert result.exit_code == 0
    assert "Copy file content to clipboard" in result.stdout


def test_undo_command_help() -> None:
    """Test undo command help."""
    result = runner.invoke(app, ["undo", "--help"])
    assert result.exit_code == 0
    assert "Undo a paste or append operation" in result.stdout


@patch("pacte.clipboard.pyperclip.paste")
@patch("pacte.cli.HistoryManager")
def test_paste_command_new_file(
    mock_history: MagicMock, mock_clipboard: MagicMock, tmp_path: Path
) -> None:
    """Test pasting to a new file."""
    mock_clipboard.return_value = "test content"
    mock_history_instance = MagicMock()
    mock_history.return_value = mock_history_instance

    file_path = tmp_path / "test.txt"

    result = runner.invoke(app, ["paste", str(file_path)])

    assert result.exit_code == 0
    assert file_path.exists()
    assert file_path.read_text(encoding="utf-8") == "test content"
    assert "Created file" in result.stdout
    assert "Pasted clipboard content" in result.stdout


@patch("pacte.clipboard.pyperclip.paste")
@patch("pacte.cli.HistoryManager")
def test_paste_command_new_file_no_create_flag(
    mock_history: MagicMock, mock_clipboard: MagicMock, tmp_path: Path
) -> None:
    """Test pasting to a new file with --no-create flag fails."""
    mock_clipboard.return_value = "test content"
    mock_history_instance = MagicMock()
    mock_history.return_value = mock_history_instance

    file_path = tmp_path / "test.txt"

    result = runner.invoke(app, ["paste", str(file_path), "--no-create"])

    assert result.exit_code == 3  # FileOperationError exit code
    assert not file_path.exists()
    assert "File does not exist" in result.stdout
    assert "Use without --no-create to create it" in result.stdout


@patch("pacte.clipboard.pyperclip.paste")
@patch("pacte.cli.HistoryManager")
def test_paste_command_existing_file_no_create_flag(
    mock_history: MagicMock, mock_clipboard: MagicMock, tmp_path: Path
) -> None:
    """Test pasting to an existing file with --no-create flag succeeds."""
    mock_clipboard.return_value = "new content"
    mock_history_instance = MagicMock()
    mock_history.return_value = mock_history_instance

    file_path = tmp_path / "test.txt"
    file_path.write_text("old content", encoding="utf-8")

    result = runner.invoke(app, ["paste", str(file_path), "--no-create", "--force"])

    assert result.exit_code == 0
    assert file_path.exists()
    assert file_path.read_text(encoding="utf-8") == "new content"
    assert "Created file" not in result.stdout  # Should not show creation message
    assert "Pasted clipboard content" in result.stdout


@patch("pacte.clipboard.pyperclip.paste")
@patch("pacte.cli.HistoryManager")
def test_paste_command_creates_parent_directories(
    mock_history: MagicMock, mock_clipboard: MagicMock, tmp_path: Path
) -> None:
    """Test pasting to a file in non-existent directories creates them."""
    mock_clipboard.return_value = "test content"
    mock_history_instance = MagicMock()
    mock_history.return_value = mock_history_instance

    file_path = tmp_path / "new" / "nested" / "dirs" / "test.txt"

    result = runner.invoke(app, ["paste", str(file_path)])

    assert result.exit_code == 0
    assert file_path.exists()
    assert file_path.read_text(encoding="utf-8") == "test content"
    assert "Created directory" in result.stdout
    assert "Created file" in result.stdout
    assert "Pasted clipboard content" in result.stdout


@patch("pacte.clipboard.pyperclip.paste")
@patch("pacte.cli.HistoryManager")
def test_paste_command_no_create_fails_with_missing_directory(
    mock_history: MagicMock, mock_clipboard: MagicMock, tmp_path: Path
) -> None:
    """Test pasting with --no-create fails when file doesn't exist even if directory exists."""
    mock_clipboard.return_value = "test content"
    mock_history_instance = MagicMock()
    mock_history.return_value = mock_history_instance

    # Create directory but not file
    dir_path = tmp_path / "existing_dir"
    dir_path.mkdir()
    file_path = dir_path / "test.txt"

    result = runner.invoke(app, ["paste", str(file_path), "--no-create"])

    assert result.exit_code == 3  # FileOperationError exit code
    assert not file_path.exists()
    assert "File does not exist" in result.stdout


@patch("pacte.clipboard.pyperclip.paste")
@patch("pacte.cli.HistoryManager")
def test_append_command(mock_history: MagicMock, mock_clipboard: MagicMock, tmp_path: Path) -> None:
    """Test appending to a file."""
    mock_clipboard.return_value = "new content"
    mock_history_instance = MagicMock()
    mock_history.return_value = mock_history_instance

    file_path = tmp_path / "test.txt"
    file_path.write_text("existing", encoding="utf-8")

    result = runner.invoke(app, ["append", str(file_path)])

    assert result.exit_code == 0
    content = file_path.read_text(encoding="utf-8")
    assert content == "existing\nnew content"
    assert "Appended clipboard content" in result.stdout


@patch("pacte.clipboard.pyperclip.copy")
def test_copy_command(mock_clipboard: MagicMock, tmp_path: Path) -> None:
    """Test copying file to clipboard."""
    file_path = tmp_path / "test.txt"
    file_path.write_text("file content", encoding="utf-8")

    result = runner.invoke(app, ["copy", str(file_path)])

    assert result.exit_code == 0
    mock_clipboard.assert_called_once_with("file content")
    assert "Copied" in result.stdout


@patch("pacte.cli.HistoryManager")
def test_undo_command_list(mock_history: MagicMock) -> None:
    """Test undo --list command."""
    mock_history_instance = MagicMock()
    mock_history_instance.get_operations.return_value = []
    mock_history.return_value = mock_history_instance

    result = runner.invoke(app, ["undo", "--list"])

    assert result.exit_code == 0


@patch("pacte.clipboard.pyperclip.paste")
def test_paste_command_empty_clipboard(mock_clipboard: MagicMock, tmp_path: Path) -> None:
    """Test pasting with empty clipboard."""
    mock_clipboard.return_value = ""
    file_path = tmp_path / "test.txt"

    result = runner.invoke(app, ["paste", str(file_path)])

    assert result.exit_code == 2  # ClipboardError exit code
    assert "Clipboard is empty" in result.stdout


@patch("pacte.clipboard.pyperclip.paste")
@patch("pacte.cli.HistoryManager")
def test_paste_command_user_cancellation(
    mock_history: MagicMock, mock_clipboard: MagicMock, tmp_path: Path
) -> None:
    """Test user cancellation on paste confirmation."""
    mock_clipboard.return_value = "test content"

    file_path = tmp_path / "test.txt"
    file_path.write_text("existing", encoding="utf-8")

    # Simulate user saying 'no' to confirmation
    result = runner.invoke(app, ["paste", str(file_path)], input="n\n")

    assert result.exit_code == 5  # User cancelled
    assert "Operation cancelled" in result.stdout
    assert file_path.read_text(encoding="utf-8") == "existing"


@patch("pacte.clipboard.pyperclip.paste")
@patch("pacte.cli.HistoryManager")
def test_paste_command_existing_file_with_backup(
    mock_history: MagicMock, mock_clipboard: MagicMock, tmp_path: Path
) -> None:
    """Test pasting to existing file creates backup."""
    mock_clipboard.return_value = "new content"
    mock_history_instance = MagicMock()
    mock_history.return_value = mock_history_instance

    file_path = tmp_path / "test.txt"
    file_path.write_text("old content", encoding="utf-8")

    result = runner.invoke(app, ["paste", str(file_path), "--force"])

    assert result.exit_code == 0
    assert "Backed up to" in result.stdout
    assert file_path.read_text(encoding="utf-8") == "new content"

    # Check backup was created
    backup_files = list(tmp_path.glob("test.txt.*.bak"))
    assert len(backup_files) == 1


@patch("pacte.clipboard.pyperclip.paste")
@patch("pacte.cli.HistoryManager")
def test_paste_command_no_backup_flag(
    mock_history: MagicMock, mock_clipboard: MagicMock, tmp_path: Path
) -> None:
    """Test pasting with --no-backup flag skips backup."""
    mock_clipboard.return_value = "new content"
    mock_history_instance = MagicMock()
    mock_history.return_value = mock_history_instance

    file_path = tmp_path / "test.txt"
    file_path.write_text("old content", encoding="utf-8")

    result = runner.invoke(app, ["paste", str(file_path), "--force", "--no-backup"])

    assert result.exit_code == 0
    assert "Backed up to" not in result.stdout

    # Check no backup was created
    backup_files = list(tmp_path.glob("test.txt.*.bak"))
    assert len(backup_files) == 0


@patch("pacte.clipboard.pyperclip.paste")
def test_append_command_empty_clipboard(mock_clipboard: MagicMock, tmp_path: Path) -> None:
    """Test appending with empty clipboard."""
    mock_clipboard.return_value = ""
    file_path = tmp_path / "test.txt"

    result = runner.invoke(app, ["append", str(file_path)])

    assert result.exit_code == 2  # ClipboardError exit code
    assert "Clipboard is empty" in result.stdout


@patch("pacte.clipboard.pyperclip.paste")
@patch("pacte.cli.HistoryManager")
def test_append_command_no_newline(
    mock_history: MagicMock, mock_clipboard: MagicMock, tmp_path: Path
) -> None:
    """Test appending without newline."""
    mock_clipboard.return_value = "new"
    mock_history_instance = MagicMock()
    mock_history.return_value = mock_history_instance

    file_path = tmp_path / "test.txt"
    file_path.write_text("old", encoding="utf-8")

    result = runner.invoke(app, ["append", str(file_path), "--no-newline"])

    assert result.exit_code == 0
    assert file_path.read_text(encoding="utf-8") == "oldnew"


@patch("pacte.clipboard.pyperclip.paste")
@patch("pacte.cli.HistoryManager")
def test_append_command_with_backup(
    mock_history: MagicMock, mock_clipboard: MagicMock, tmp_path: Path
) -> None:
    """Test appending creates backup."""
    mock_clipboard.return_value = "new content"
    mock_history_instance = MagicMock()
    mock_history.return_value = mock_history_instance

    file_path = tmp_path / "test.txt"
    file_path.write_text("old content", encoding="utf-8")

    result = runner.invoke(app, ["append", str(file_path)])

    assert result.exit_code == 0
    assert "Backed up to" in result.stdout

    # Check backup was created
    backup_files = list(tmp_path.glob("test.txt.*.bak"))
    assert len(backup_files) == 1


def test_copy_command_file_not_exists(tmp_path: Path) -> None:
    """Test copying non-existent file."""
    file_path = tmp_path / "nonexistent.txt"

    result = runner.invoke(app, ["copy", str(file_path)])

    # Should fail with non-zero exit code
    assert result.exit_code != 0


@patch("pacte.clipboard.pyperclip.copy")
def test_copy_command_with_text_file(mock_clipboard: MagicMock, tmp_path: Path) -> None:
    """Test copying regular text file."""
    file_path = tmp_path / "test.txt"
    content = "test content with unicode: café"
    file_path.write_text(content, encoding="utf-8")

    result = runner.invoke(app, ["copy", str(file_path)])

    assert result.exit_code == 0
    mock_clipboard.assert_called_once_with(content)


@patch("pacte.cli.HistoryManager")
def test_undo_command_no_history(mock_history: MagicMock) -> None:
    """Test undo with no operations in history."""
    mock_history_instance = MagicMock()
    mock_history_instance.get_operations.return_value = []
    mock_history.return_value = mock_history_instance

    result = runner.invoke(app, ["undo"])

    assert result.exit_code == 0
    assert "No operations found" in result.stdout


@patch("pacte.clipboard.pyperclip.paste")
def test_paste_command_clipboard_error(mock_clipboard: MagicMock, tmp_path: Path) -> None:
    """Test paste command with ClipboardError."""
    from pacte.exceptions import ClipboardError

    mock_clipboard.side_effect = ClipboardError("Failed to access clipboard")
    file_path = tmp_path / "test.txt"

    result = runner.invoke(app, ["paste", str(file_path)])

    assert result.exit_code == 2
    assert "Failed to access clipboard" in result.stdout


@patch("pacte.clipboard.pyperclip.paste")
@patch("pacte.cli.HistoryManager")
def test_paste_command_history_error(
    mock_history: MagicMock, mock_clipboard: MagicMock, tmp_path: Path
) -> None:
    """Test paste command with HistoryError."""
    from pacte.exceptions import HistoryError

    mock_clipboard.return_value = "test content"
    mock_history_instance = MagicMock()
    mock_history_instance.add_operation.side_effect = HistoryError("Failed to save history")
    mock_history.return_value = mock_history_instance

    file_path = tmp_path / "test.txt"

    result = runner.invoke(app, ["paste", str(file_path)])

    assert result.exit_code == 4
    assert "Failed to save history" in result.stdout


@patch("pacte.clipboard.pyperclip.paste")
@patch("pacte.cli.load_config")
def test_paste_command_pacte_error(
    mock_config: MagicMock, mock_clipboard: MagicMock, tmp_path: Path
) -> None:
    """Test paste command with generic PacteError from config loading."""
    from pacte.exceptions import PacteError

    # Make config loading fail with generic PacteError
    mock_config.side_effect = PacteError("Generic error")
    file_path = tmp_path / "test.txt"

    result = runner.invoke(app, ["paste", str(file_path)])

    assert result.exit_code == 1
    assert "Generic error" in result.stdout


@patch("pacte.clipboard.pyperclip.paste")
def test_append_command_clipboard_error(mock_clipboard: MagicMock, tmp_path: Path) -> None:
    """Test append command with ClipboardError."""
    from pacte.exceptions import ClipboardError

    mock_clipboard.side_effect = ClipboardError("Failed to access clipboard")
    file_path = tmp_path / "test.txt"
    file_path.write_text("existing", encoding="utf-8")

    result = runner.invoke(app, ["append", str(file_path)])

    assert result.exit_code == 2
    assert "Failed to access clipboard" in result.stdout


@patch("pacte.clipboard.pyperclip.paste")
@patch("pacte.cli.append_to_file")
def test_append_command_file_operation_error(
    mock_append: MagicMock, mock_clipboard: MagicMock, tmp_path: Path
) -> None:
    """Test append command with FileOperationError."""
    from pacte.exceptions import FileOperationError

    mock_clipboard.return_value = "content"
    mock_append.side_effect = FileOperationError("Failed to write to file")

    file_path = tmp_path / "test.txt"
    file_path.write_text("existing", encoding="utf-8")

    result = runner.invoke(app, ["append", str(file_path)])

    assert result.exit_code == 3
    assert "Failed to write to file" in result.stdout


@patch("pacte.clipboard.pyperclip.paste")
@patch("pacte.cli.HistoryManager")
def test_append_command_history_error(
    mock_history: MagicMock, mock_clipboard: MagicMock, tmp_path: Path
) -> None:
    """Test append command with HistoryError."""
    from pacte.exceptions import HistoryError

    mock_clipboard.return_value = "content"
    mock_history_instance = MagicMock()
    mock_history_instance.add_operation.side_effect = HistoryError("Failed to save history")
    mock_history.return_value = mock_history_instance

    file_path = tmp_path / "test.txt"
    file_path.write_text("existing", encoding="utf-8")

    result = runner.invoke(app, ["append", str(file_path)])

    assert result.exit_code == 4
    assert "Failed to save history" in result.stdout


@patch("pacte.clipboard.pyperclip.paste")
@patch("pacte.cli.load_config")
def test_append_command_pacte_error(
    mock_config: MagicMock, mock_clipboard: MagicMock, tmp_path: Path
) -> None:
    """Test append command with generic PacteError from config loading."""
    from pacte.exceptions import PacteError

    # Make config loading fail with generic PacteError
    mock_config.side_effect = PacteError("Generic error")
    file_path = tmp_path / "test.txt"

    result = runner.invoke(app, ["append", str(file_path)])

    assert result.exit_code == 1
    assert "Generic error" in result.stdout


@patch("pacte.clipboard.pyperclip.copy")
@patch("pacte.cli.is_binary_file")
def test_copy_command_binary_file_cancelled(
    mock_is_binary: MagicMock, mock_clipboard: MagicMock, tmp_path: Path
) -> None:
    """Test copy command with binary file and user cancellation."""
    mock_is_binary.return_value = True

    file_path = tmp_path / "binary.bin"
    file_path.write_bytes(b"\x00\x01\x02")

    result = runner.invoke(app, ["copy", str(file_path)], input="n\n")

    assert result.exit_code == 5
    assert "Operation cancelled" in result.stdout
    mock_clipboard.assert_not_called()


@patch("pacte.clipboard.pyperclip.copy")
@patch("pacte.cli.is_binary_file")
def test_copy_command_binary_file_confirmed(
    mock_is_binary: MagicMock, mock_clipboard: MagicMock, tmp_path: Path
) -> None:
    """Test copy command with binary file and user confirmation."""
    mock_is_binary.return_value = True

    file_path = tmp_path / "binary.txt"
    file_path.write_text("actually text", encoding="utf-8")

    result = runner.invoke(app, ["copy", str(file_path)], input="y\n")

    assert result.exit_code == 0
    assert "Copied" in result.stdout
    mock_clipboard.assert_called_once()


@patch("pacte.clipboard.pyperclip.copy")
def test_copy_command_clipboard_error(mock_clipboard: MagicMock, tmp_path: Path) -> None:
    """Test copy command with ClipboardError."""
    from pacte.exceptions import ClipboardError

    file_path = tmp_path / "test.txt"
    file_path.write_text("content", encoding="utf-8")

    mock_clipboard.side_effect = ClipboardError("Failed to access clipboard")

    result = runner.invoke(app, ["copy", str(file_path)])

    assert result.exit_code == 2
    assert "Failed to access clipboard" in result.stdout


@patch("pacte.cli.read_from_file")
@patch("pacte.clipboard.pyperclip.copy")
def test_copy_command_file_operation_error(
    mock_clipboard: MagicMock, mock_read: MagicMock, tmp_path: Path
) -> None:
    """Test copy command with FileOperationError."""
    from pacte.exceptions import FileOperationError

    file_path = tmp_path / "test.txt"
    file_path.write_text("content", encoding="utf-8")

    mock_read.side_effect = FileOperationError("Failed to read file")

    result = runner.invoke(app, ["copy", str(file_path)])

    assert result.exit_code == 3
    assert "Failed to read file" in result.stdout


@patch("pacte.clipboard.pyperclip.copy")
@patch("pacte.cli.is_binary_file")
def test_copy_command_pacte_error(
    mock_is_binary: MagicMock, mock_clipboard: MagicMock, tmp_path: Path
) -> None:
    """Test copy command with generic PacteError from is_binary_file."""
    from pacte.exceptions import PacteError

    file_path = tmp_path / "test.txt"
    file_path.write_text("content", encoding="utf-8")

    # Make is_binary_file raise generic PacteError
    mock_is_binary.side_effect = PacteError("Generic error")

    result = runner.invoke(app, ["copy", str(file_path)])

    assert result.exit_code == 1
    assert "Generic error" in result.stdout


@patch("pacte.cli.select_operation_to_undo")
@patch("pacte.cli.HistoryManager")
def test_undo_command_user_cancels_selection(
    mock_history: MagicMock, mock_select: MagicMock, tmp_path: Path
) -> None:
    """Test undo command when user cancels operation selection."""
    from pacte.models import Operation

    mock_history_instance = MagicMock()
    operations = [
        Operation(
            id="op1",
            timestamp="2024-01-01T10:00:00",
            operation_type="paste",
            target_path=str(tmp_path / "test.txt"),
            backup_path=None,
            content_preview="Content",
        )
    ]
    mock_history_instance.get_operations.return_value = operations
    mock_history.return_value = mock_history_instance

    # User cancels selection
    mock_select.return_value = None

    result = runner.invoke(app, ["undo"])

    assert result.exit_code == 5
    assert "Operation cancelled" in result.stdout


@patch("pacte.cli.select_operation_to_undo")
@patch("pacte.cli.HistoryManager")
def test_undo_command_with_backup(
    mock_history: MagicMock, mock_select: MagicMock, tmp_path: Path
) -> None:
    """Test undo command restores from backup."""
    from pacte.models import Operation

    # Create test files
    target_path = tmp_path / "test.txt"
    backup_path = tmp_path / "test.txt.backup.bak"
    target_path.write_text("modified content", encoding="utf-8")
    backup_path.write_text("original content", encoding="utf-8")

    operation = Operation(
        id="op1",
        timestamp="2024-01-01T10:00:00",
        operation_type="paste",
        target_path=str(target_path),
        backup_path=str(backup_path),
        content_preview="Content",
    )

    mock_history_instance = MagicMock()
    mock_history_instance.get_operations.return_value = [operation]
    mock_history.return_value = mock_history_instance

    mock_select.return_value = operation

    result = runner.invoke(app, ["undo"])

    assert result.exit_code == 0
    assert "Restored" in result.stdout
    assert target_path.read_text(encoding="utf-8") == "original content"
    assert not backup_path.exists()


@patch("pacte.cli.select_operation_to_undo")
@patch("pacte.cli.HistoryManager")
def test_undo_command_delete_file(
    mock_history: MagicMock, mock_select: MagicMock, tmp_path: Path
) -> None:
    """Test undo command deletes file when no backup exists."""
    from pacte.models import Operation

    # Create test file
    target_path = tmp_path / "test.txt"
    target_path.write_text("content", encoding="utf-8")

    operation = Operation(
        id="op1",
        timestamp="2024-01-01T10:00:00",
        operation_type="paste",
        target_path=str(target_path),
        backup_path=None,
        content_preview="Content",
    )

    mock_history_instance = MagicMock()
    mock_history_instance.get_operations.return_value = [operation]
    mock_history.return_value = mock_history_instance

    mock_select.return_value = operation

    result = runner.invoke(app, ["undo"])

    assert result.exit_code == 0
    assert "Deleted" in result.stdout
    assert not target_path.exists()


@patch("pacte.cli.HistoryManager")
def test_undo_command_last_flag(mock_history: MagicMock, tmp_path: Path) -> None:
    """Test undo command with --last flag."""
    from pacte.models import Operation

    target_path = tmp_path / "test.txt"
    target_path.write_text("content", encoding="utf-8")

    operation = Operation(
        id="op1",
        timestamp="2024-01-01T10:00:00",
        operation_type="paste",
        target_path=str(target_path),
        backup_path=None,
        content_preview="Content",
    )

    mock_history_instance = MagicMock()
    mock_history_instance.get_operations.return_value = [operation]
    mock_history.return_value = mock_history_instance

    result = runner.invoke(app, ["undo", "--last"])

    assert result.exit_code == 0
    assert "Deleted" in result.stdout
    assert not target_path.exists()


@patch("pacte.cli.restore_from_backup")
@patch("pacte.cli.select_operation_to_undo")
@patch("pacte.cli.HistoryManager")
def test_undo_command_file_operation_error(
    mock_history: MagicMock, mock_select: MagicMock, mock_restore: MagicMock, tmp_path: Path
) -> None:
    """Test undo command with FileOperationError."""
    from pacte.exceptions import FileOperationError
    from pacte.models import Operation

    backup_path = tmp_path / "backup.bak"
    operation = Operation(
        id="op1",
        timestamp="2024-01-01T10:00:00",
        operation_type="paste",
        target_path=str(tmp_path / "test.txt"),
        backup_path=str(backup_path),
        content_preview="Content",
    )

    mock_history_instance = MagicMock()
    mock_history_instance.get_operations.return_value = [operation]
    mock_history.return_value = mock_history_instance

    mock_select.return_value = operation
    mock_restore.side_effect = FileOperationError("Failed to restore")

    result = runner.invoke(app, ["undo"])

    assert result.exit_code == 3
    assert "Failed to restore" in result.stdout


@patch("pacte.cli.select_operation_to_undo")
@patch("pacte.cli.HistoryManager")
def test_undo_command_history_error(
    mock_history: MagicMock, mock_select: MagicMock, tmp_path: Path
) -> None:
    """Test undo command with HistoryError."""
    from pacte.exceptions import HistoryError
    from pacte.models import Operation

    target_path = tmp_path / "test.txt"
    target_path.write_text("content", encoding="utf-8")

    operation = Operation(
        id="op1",
        timestamp="2024-01-01T10:00:00",
        operation_type="paste",
        target_path=str(target_path),
        backup_path=None,
        content_preview="Content",
    )

    mock_history_instance = MagicMock()
    mock_history_instance.get_operations.return_value = [operation]
    mock_history_instance.remove_operation.side_effect = HistoryError(
        "Failed to remove from history"
    )
    mock_history.return_value = mock_history_instance

    mock_select.return_value = operation

    result = runner.invoke(app, ["undo"])

    assert result.exit_code == 4
    assert "Failed to remove from history" in result.stdout


@patch("pacte.cli.select_operation_to_undo")
@patch("pacte.cli.HistoryManager")
def test_undo_command_pacte_error(
    mock_history: MagicMock, mock_select: MagicMock, tmp_path: Path
) -> None:
    """Test undo command with generic PacteError."""
    from pacte.exceptions import PacteError
    from pacte.models import Operation

    operation = Operation(
        id="op1",
        timestamp="2024-01-01T10:00:00",
        operation_type="paste",
        target_path=str(tmp_path / "test.txt"),
        backup_path=None,
        content_preview="Content",
    )

    mock_history_instance = MagicMock()
    mock_history_instance.get_operations.return_value = [operation]
    mock_history.return_value = mock_history_instance

    mock_select.side_effect = PacteError("Generic error")

    result = runner.invoke(app, ["undo"])

    assert result.exit_code == 1
    assert "Generic error" in result.stdout

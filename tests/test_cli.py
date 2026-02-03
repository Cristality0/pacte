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

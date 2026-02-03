"""Integration tests for end-to-end workflows."""

from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from pacte.cli import app

runner = CliRunner()


@patch("pacte.clipboard.pyperclip.paste")
@patch("pacte.clipboard.pyperclip.copy")
def test_paste_and_copy_workflow(
    mock_set_clipboard: object, mock_get_clipboard: object, tmp_path: Path
) -> None:
    """Test pasting content and then copying it back."""
    mock_get_clipboard.return_value = "workflow test content"  # type: ignore

    file_path = tmp_path / "workflow.txt"

    # Step 1: Paste clipboard to file
    result = runner.invoke(app, ["paste", str(file_path)])
    assert result.exit_code == 0
    assert file_path.exists()

    # Step 2: Copy file back to clipboard
    result = runner.invoke(app, ["copy", str(file_path)])
    assert result.exit_code == 0
    mock_set_clipboard.assert_called_once_with("workflow test content")  # type: ignore


@patch("pacte.clipboard.pyperclip.paste")
def test_paste_append_workflow(mock_clipboard: object, tmp_path: Path) -> None:
    """Test pasting and then appending content."""
    file_path = tmp_path / "workflow.txt"

    # Step 1: Paste initial content
    mock_clipboard.return_value = "First line"  # type: ignore
    result = runner.invoke(app, ["paste", str(file_path)])
    assert result.exit_code == 0

    # Step 2: Append more content
    mock_clipboard.return_value = "Second line"  # type: ignore
    result = runner.invoke(app, ["append", str(file_path)])
    assert result.exit_code == 0

    # Verify content
    content = file_path.read_text(encoding="utf-8")
    assert content == "First line\nSecond line"


@patch("pacte.clipboard.pyperclip.paste")
def test_paste_undo_workflow(mock_clipboard: object, tmp_path: Path) -> None:
    """Test pasting and undoing with last flag."""
    mock_clipboard.return_value = "content to undo"  # type: ignore

    file_path = tmp_path / "undo_test.txt"

    # Step 1: Paste content
    result = runner.invoke(app, ["paste", str(file_path)])
    assert result.exit_code == 0
    assert file_path.exists()

    # Step 2: Undo last operation
    result = runner.invoke(app, ["undo", "--last"])
    assert result.exit_code == 0

    # File should be deleted (it was newly created)
    assert not file_path.exists()


@patch("pacte.clipboard.pyperclip.paste")
def test_overwrite_with_backup_and_undo(mock_clipboard: object, tmp_path: Path) -> None:
    """Test overwriting file with backup and then undoing."""
    file_path = tmp_path / "backup_test.txt"

    # Create initial file
    file_path.write_text("original content", encoding="utf-8")

    # Overwrite with clipboard
    mock_clipboard.return_value = "new content"  # type: ignore
    result = runner.invoke(app, ["paste", str(file_path), "--force"])
    assert result.exit_code == 0
    assert file_path.read_text(encoding="utf-8") == "new content"
    assert "Backed up" in result.stdout

    # Undo operation
    result = runner.invoke(app, ["undo", "--last"])
    assert result.exit_code == 0

    # Original content should be restored
    assert file_path.read_text(encoding="utf-8") == "original content"


@patch("pacte.clipboard.pyperclip.paste")
def test_multiple_operations_history(mock_clipboard: object, tmp_path: Path) -> None:
    """Test multiple operations are tracked in history."""
    # Perform multiple paste operations
    for i in range(3):
        file_path = tmp_path / f"file{i}.txt"
        mock_clipboard.return_value = f"content {i}"  # type: ignore
        result = runner.invoke(app, ["paste", str(file_path)])
        assert result.exit_code == 0

    # Check history list
    result = runner.invoke(app, ["undo", "--list"])
    assert result.exit_code == 0
    assert "content 0" in result.stdout
    assert "content 1" in result.stdout
    assert "content 2" in result.stdout

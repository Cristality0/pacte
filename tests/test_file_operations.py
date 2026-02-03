"""Tests for file operations."""

from pathlib import Path
from unittest.mock import patch

import pytest

from pacte.exceptions import FileOperationError
from pacte.file_operations import (
    append_to_file,
    create_backup,
    delete_file,
    is_binary_file,
    read_from_file,
    restore_from_backup,
    write_to_file,
)


def test_write_to_file(tmp_path: Path) -> None:
    """Test writing content to file."""
    file_path = tmp_path / "test.txt"
    content = "Hello, World!"

    size = write_to_file(file_path, content)

    assert file_path.exists()
    assert file_path.read_text(encoding="utf-8") == content
    assert size > 0


def test_write_to_file_overwrite(tmp_path: Path) -> None:
    """Test overwriting existing file."""
    file_path = tmp_path / "test.txt"
    file_path.write_text("original", encoding="utf-8")

    write_to_file(file_path, "new content")

    assert file_path.read_text(encoding="utf-8") == "new content"


def test_append_to_file_new(tmp_path: Path) -> None:
    """Test appending to new file."""
    file_path = tmp_path / "test.txt"
    content = "First line"

    size = append_to_file(file_path, content)

    assert file_path.exists()
    assert file_path.read_text(encoding="utf-8") == content
    assert size > 0


def test_append_to_file_existing(tmp_path: Path) -> None:
    """Test appending to existing file."""
    file_path = tmp_path / "test.txt"
    file_path.write_text("First line", encoding="utf-8")

    append_to_file(file_path, "Second line")

    content = file_path.read_text(encoding="utf-8")
    assert content == "First line\nSecond line"


def test_append_to_file_no_newline(tmp_path: Path) -> None:
    """Test appending without newline."""
    file_path = tmp_path / "test.txt"
    file_path.write_text("First", encoding="utf-8")

    append_to_file(file_path, "Second", add_newline=False)

    assert file_path.read_text(encoding="utf-8") == "FirstSecond"


def test_read_from_file(tmp_path: Path) -> None:
    """Test reading file content."""
    file_path = tmp_path / "test.txt"
    content = "Test content"
    file_path.write_text(content, encoding="utf-8")

    result = read_from_file(file_path)

    assert result == content


def test_read_from_file_not_exists(tmp_path: Path) -> None:
    """Test reading non-existent file."""
    file_path = tmp_path / "missing.txt"

    with pytest.raises(FileOperationError, match="File does not exist"):
        read_from_file(file_path)


def test_create_backup(tmp_path: Path) -> None:
    """Test creating file backup."""
    file_path = tmp_path / "test.txt"
    content = "Original content"
    file_path.write_text(content, encoding="utf-8")

    backup_path = create_backup(file_path)

    assert backup_path.exists()
    assert backup_path.name.startswith("test.txt.")
    assert backup_path.name.endswith(".bak")
    assert backup_path.read_text(encoding="utf-8") == content


def test_create_backup_not_exists(tmp_path: Path) -> None:
    """Test creating backup of non-existent file."""
    file_path = tmp_path / "missing.txt"

    with pytest.raises(FileOperationError, match="File does not exist"):
        create_backup(file_path)


def test_restore_from_backup(tmp_path: Path) -> None:
    """Test restoring file from backup."""
    target_path = tmp_path / "test.txt"
    backup_path = tmp_path / "test.txt.backup.bak"

    # Create files
    target_path.write_text("modified", encoding="utf-8")
    backup_path.write_text("original", encoding="utf-8")

    restore_from_backup(backup_path, target_path)

    assert target_path.read_text(encoding="utf-8") == "original"
    assert not backup_path.exists()  # Backup should be deleted


def test_restore_from_backup_missing(tmp_path: Path) -> None:
    """Test restoring from missing backup."""
    backup_path = tmp_path / "missing.bak"
    target_path = tmp_path / "test.txt"

    with pytest.raises(FileOperationError, match="Backup file does not exist"):
        restore_from_backup(backup_path, target_path)


def test_delete_file(tmp_path: Path) -> None:
    """Test deleting a file."""
    file_path = tmp_path / "test.txt"
    file_path.write_text("content", encoding="utf-8")

    delete_file(file_path)

    assert not file_path.exists()


def test_delete_file_not_exists(tmp_path: Path) -> None:
    """Test deleting non-existent file."""
    file_path = tmp_path / "missing.txt"

    with pytest.raises(FileOperationError, match="File does not exist"):
        delete_file(file_path)


def test_is_binary_file_text(tmp_path: Path) -> None:
    """Test detecting text file."""
    file_path = tmp_path / "test.txt"
    file_path.write_text("Hello, World!", encoding="utf-8")

    assert is_binary_file(file_path) is False


def test_is_binary_file_binary(tmp_path: Path) -> None:
    """Test detecting binary file."""
    file_path = tmp_path / "test.bin"
    file_path.write_bytes(b"\x00\x01\x02\xff\xfe")

    assert is_binary_file(file_path) is True


def test_write_to_file_custom_encoding(tmp_path: Path) -> None:
    """Test writing file with custom encoding."""
    file_path = tmp_path / "test.txt"
    content = "Héllo, Wörld!"

    write_to_file(file_path, content, encoding="latin1")

    assert file_path.read_text(encoding="latin1") == content


def test_write_to_file_error_handling(tmp_path: Path) -> None:
    """Test write_to_file error handling for invalid paths."""
    # Create a directory to trigger an error
    dir_path = tmp_path / "dir"
    dir_path.mkdir()

    with pytest.raises(FileOperationError, match="Failed to write to file"):
        write_to_file(dir_path, "content")


def test_append_to_file_empty_file(tmp_path: Path) -> None:
    """Test appending to empty file doesn't add unnecessary newline."""
    file_path = tmp_path / "test.txt"
    file_path.write_text("", encoding="utf-8")

    append_to_file(file_path, "content", add_newline=True)

    # Empty file should not get a leading newline
    assert file_path.read_text(encoding="utf-8") == "content"


def test_append_to_file_custom_encoding(tmp_path: Path) -> None:
    """Test appending with custom encoding."""
    file_path = tmp_path / "test.txt"
    file_path.write_text("First", encoding="utf-16")

    append_to_file(file_path, "Second", encoding="utf-16")

    content = file_path.read_text(encoding="utf-16")
    assert "First" in content
    assert "Second" in content


def test_read_from_file_unicode_decode_error(tmp_path: Path) -> None:
    """Test reading binary file as text raises proper error."""
    file_path = tmp_path / "binary.bin"
    file_path.write_bytes(b"\x00\x01\xff\xfe")

    with pytest.raises(FileOperationError, match="Failed to decode file"):
        read_from_file(file_path, encoding="utf-8")


def test_read_from_file_custom_encoding(tmp_path: Path) -> None:
    """Test reading file with custom encoding."""
    file_path = tmp_path / "test.txt"
    content = "Spëcial chàrs"
    file_path.write_text(content, encoding="latin1")

    result = read_from_file(file_path, encoding="latin1")

    assert result == content


def test_create_backup_preserves_binary_content(tmp_path: Path) -> None:
    """Test backup preserves binary content exactly."""
    file_path = tmp_path / "binary.bin"
    binary_content = b"\x00\x01\x02\x03\xff\xfe\xfd"
    file_path.write_bytes(binary_content)

    backup_path = create_backup(file_path)

    assert backup_path.read_bytes() == binary_content


def test_restore_from_backup_error_handling(tmp_path: Path) -> None:
    """Test restore_from_backup error handling."""
    backup_path = tmp_path / "backup.bak"
    backup_path.write_text("content", encoding="utf-8")

    # Try to restore to a directory (invalid)
    dir_path = tmp_path / "dir"
    dir_path.mkdir()

    with pytest.raises(FileOperationError, match="Failed to restore from backup"):
        restore_from_backup(backup_path, dir_path)


def test_delete_file_permission_error(tmp_path: Path) -> None:
    """Test delete_file handles permission errors."""
    file_path = tmp_path / "test.txt"
    file_path.write_text("content", encoding="utf-8")

    # Use patch to mock Path.unlink at the class level for this specific test
    with (
        patch.object(Path, "unlink", side_effect=PermissionError("Permission denied")),
        pytest.raises(FileOperationError, match="Failed to delete file"),
    ):
        delete_file(file_path)


def test_is_binary_file_large_text_file(tmp_path: Path) -> None:
    """Test binary detection with large text file."""
    file_path = tmp_path / "large.txt"
    # Create a file larger than the sample size
    large_content = "a" * 10000
    file_path.write_text(large_content, encoding="utf-8")

    assert is_binary_file(file_path) is False


def test_is_binary_file_mixed_content(tmp_path: Path) -> None:
    """Test binary detection with mixed binary/text content."""
    file_path = tmp_path / "mixed.dat"
    # Create file with null bytes that should be detected as binary
    # Use enough binary content to be detected
    mixed_content = b"\x00\x01\x02\xff\xfe\xfd\x00Some text"
    file_path.write_bytes(mixed_content)

    assert is_binary_file(file_path) is True


def test_is_binary_file_custom_sample_size(tmp_path: Path) -> None:
    """Test binary detection with custom sample size."""
    file_path = tmp_path / "test.txt"
    file_path.write_text("Short text", encoding="utf-8")

    # Use a very small sample size
    assert is_binary_file(file_path, sample_size=5) is False

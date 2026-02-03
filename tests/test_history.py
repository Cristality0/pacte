"""Tests for history management."""

from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from pacte.exceptions import HistoryError
from pacte.history import HistoryManager


def test_history_manager_init(tmp_path: Path) -> None:
    """Test HistoryManager initialization."""
    manager = HistoryManager(history_dir=tmp_path, max_history=100)

    assert manager.history_dir == tmp_path
    assert manager.max_history == 100
    assert manager.history_file == tmp_path / "history.json"


def test_add_operation(clean_history: HistoryManager, tmp_path: Path) -> None:
    """Test adding an operation to history."""
    target_path = tmp_path / "test.txt"
    backup_path = tmp_path / "test.txt.backup.bak"

    operation = clean_history.add_operation(
        operation_type="paste",
        target_path=target_path,
        backup_path=backup_path,
        content_preview="Test content preview",
    )

    assert operation.operation_type == "paste"
    assert operation.target_path == str(target_path.absolute())
    assert operation.backup_path == str(backup_path.absolute())
    assert "Test content preview" in operation.content_preview


def test_add_operation_no_backup(clean_history: HistoryManager, tmp_path: Path) -> None:
    """Test adding an operation without backup."""
    target_path = tmp_path / "test.txt"

    operation = clean_history.add_operation(
        operation_type="paste",
        target_path=target_path,
        backup_path=None,
        content_preview="Content",
    )

    assert operation.backup_path is None


def test_get_operations_empty(clean_history: HistoryManager) -> None:
    """Test getting operations from empty history."""
    operations = clean_history.get_operations()

    assert operations == []


def test_get_operations(clean_history: HistoryManager, tmp_path: Path) -> None:
    """Test getting operations from history."""
    # Add multiple operations
    for i in range(3):
        clean_history.add_operation(
            operation_type="paste",
            target_path=tmp_path / f"test{i}.txt",
            backup_path=None,
            content_preview=f"Content {i}",
        )

    operations = clean_history.get_operations()

    assert len(operations) == 3
    # Should be newest first
    assert "Content 2" in operations[0].content_preview
    assert "Content 0" in operations[2].content_preview


def test_get_operations_with_limit(clean_history: HistoryManager, tmp_path: Path) -> None:
    """Test getting operations with limit."""
    # Add multiple operations
    for i in range(5):
        clean_history.add_operation(
            operation_type="paste",
            target_path=tmp_path / f"test{i}.txt",
            backup_path=None,
            content_preview=f"Content {i}",
        )

    operations = clean_history.get_operations(limit=2)

    assert len(operations) == 2
    assert "Content 4" in operations[0].content_preview


def test_remove_operation(clean_history: HistoryManager, tmp_path: Path) -> None:
    """Test removing an operation from history."""
    operation = clean_history.add_operation(
        operation_type="paste",
        target_path=tmp_path / "test.txt",
        backup_path=None,
        content_preview="Content",
    )

    clean_history.remove_operation(operation.id)

    operations = clean_history.get_operations()
    assert len(operations) == 0


def test_remove_operation_not_found(clean_history: HistoryManager) -> None:
    """Test removing non-existent operation."""
    with pytest.raises(HistoryError, match="Operation not found"):
        clean_history.remove_operation("non-existent-id")


def test_cleanup_old_operations(tmp_path: Path) -> None:
    """Test automatic cleanup of old operations."""
    manager = HistoryManager(history_dir=tmp_path, max_history=3)

    # Add more than max_history operations
    for i in range(5):
        manager.add_operation(
            operation_type="paste",
            target_path=tmp_path / f"test{i}.txt",
            backup_path=None,
            content_preview=f"Content {i}",
        )

    operations = manager.get_operations()

    # Should only keep max_history operations
    assert len(operations) == 3
    # Should keep newest ones
    assert "Content 4" in operations[0].content_preview
    assert "Content 3" in operations[1].content_preview
    assert "Content 2" in operations[2].content_preview


def test_history_persistence(tmp_path: Path) -> None:
    """Test that history persists across instances."""
    manager1 = HistoryManager(history_dir=tmp_path, max_history=50)

    operation = manager1.add_operation(
        operation_type="paste",
        target_path=tmp_path / "test.txt",
        backup_path=None,
        content_preview="Content",
    )

    # Create new manager instance
    manager2 = HistoryManager(history_dir=tmp_path, max_history=50)

    operations = manager2.get_operations()
    assert len(operations) == 1
    assert operations[0].id == operation.id


def test_history_manager_default_dir() -> None:
    """Test HistoryManager with default directory."""
    manager = HistoryManager(history_dir=None, max_history=50)

    # Should create directory in platformdirs location
    assert manager.history_dir.exists()
    assert "pacte" in str(manager.history_dir).lower()


def test_add_operation_truncates_preview(clean_history: HistoryManager, tmp_path: Path) -> None:
    """Test that long content previews are truncated."""
    long_content = "a" * 100

    operation = clean_history.add_operation(
        operation_type="paste",
        target_path=tmp_path / "test.txt",
        backup_path=None,
        content_preview=long_content,
    )

    # Preview should be truncated to default 50 chars + "..."
    assert len(operation.content_preview) <= 53


def test_load_history_corrupted_json(tmp_path: Path) -> None:
    """Test loading corrupted history file."""
    manager = HistoryManager(history_dir=tmp_path, max_history=50)

    # Create corrupted JSON file
    manager.history_file.write_text("{ invalid json", encoding="utf-8")

    with pytest.raises(HistoryError, match="History file is corrupted"):
        manager.get_operations()


def test_load_history_missing_operations_key(tmp_path: Path) -> None:
    """Test loading history with missing operations key."""
    manager = HistoryManager(history_dir=tmp_path, max_history=50)

    # Create history file without operations key
    manager.history_file.write_text('{"version": "1.0"}', encoding="utf-8")

    operations = manager.get_operations()

    # Should return empty list and add the missing key
    assert operations == []


def test_load_history_missing_version_key(tmp_path: Path) -> None:
    """Test loading history with missing version key."""
    manager = HistoryManager(history_dir=tmp_path, max_history=50)

    # Create history file without version key
    manager.history_file.write_text('{"operations": []}', encoding="utf-8")

    operations = manager.get_operations()

    # Should work and add default version
    assert operations == []


def test_cleanup_deletes_backup_files(tmp_path: Path) -> None:
    """Test that cleanup deletes associated backup files."""
    manager = HistoryManager(history_dir=tmp_path, max_history=2)

    # Create backup files
    backup1 = tmp_path / "backup1.bak"
    backup2 = tmp_path / "backup2.bak"
    backup3 = tmp_path / "backup3.bak"

    for backup in [backup1, backup2, backup3]:
        backup.write_text("backup content", encoding="utf-8")

    # Add operations with backups
    manager.add_operation(
        operation_type="paste",
        target_path=tmp_path / "test1.txt",
        backup_path=backup1,
        content_preview="Content 1",
    )

    manager.add_operation(
        operation_type="paste",
        target_path=tmp_path / "test2.txt",
        backup_path=backup2,
        content_preview="Content 2",
    )

    # This should trigger cleanup of the first operation
    manager.add_operation(
        operation_type="paste",
        target_path=tmp_path / "test3.txt",
        backup_path=backup3,
        content_preview="Content 3",
    )

    # backup1 should be deleted
    assert not backup1.exists()
    assert backup2.exists()
    assert backup3.exists()


def test_cleanup_handles_missing_backup_files(tmp_path: Path) -> None:
    """Test that cleanup doesn't fail if backup file is missing."""
    manager = HistoryManager(history_dir=tmp_path, max_history=2)

    # Add operations with non-existent backup paths
    manager.add_operation(
        operation_type="paste",
        target_path=tmp_path / "test1.txt",
        backup_path=tmp_path / "nonexistent1.bak",
        content_preview="Content 1",
    )

    manager.add_operation(
        operation_type="paste",
        target_path=tmp_path / "test2.txt",
        backup_path=tmp_path / "nonexistent2.bak",
        content_preview="Content 2",
    )

    # This should trigger cleanup - shouldn't raise error
    manager.add_operation(
        operation_type="paste",
        target_path=tmp_path / "test3.txt",
        backup_path=None,
        content_preview="Content 3",
    )

    operations = manager.get_operations()
    assert len(operations) == 2


def test_add_operation_append_type(clean_history: HistoryManager, tmp_path: Path) -> None:
    """Test adding an append operation."""
    operation = clean_history.add_operation(
        operation_type="append",
        target_path=tmp_path / "test.txt",
        backup_path=None,
        content_preview="Appended content",
    )

    assert operation.operation_type == "append"


def test_operations_sorted_newest_first(clean_history: HistoryManager, tmp_path: Path) -> None:
    """Test that operations are returned newest first."""
    # Mock timestamps to ensure different values without using time.sleep
    base_time = datetime(2024, 1, 1, 12, 0, 0)

    # Add operations with mocked timestamps
    for i in range(3):
        with patch("pacte.utils.datetime") as mock_dt:
            mock_dt.now.return_value = base_time.replace(second=i)
            clean_history.add_operation(
                operation_type="paste",
                target_path=tmp_path / f"test{i}.txt",
                backup_path=None,
                content_preview=f"Content {i}",
            )

    operations = clean_history.get_operations()

    # First operation should be the most recent
    assert "Content 2" in operations[0].content_preview
    assert "Content 1" in operations[1].content_preview
    assert "Content 0" in operations[2].content_preview

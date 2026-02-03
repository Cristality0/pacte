"""Tests for data models."""

from pacte.models import Config, Operation


def test_operation_creation() -> None:
    """Test creating an Operation."""
    op = Operation(
        id="test-id",
        timestamp="2024-02-02T15:30:45",
        operation_type="paste",
        target_path="/path/to/file.txt",
        backup_path="/path/to/backup.bak",
        content_preview="test content",
    )

    assert op.id == "test-id"
    assert op.timestamp == "2024-02-02T15:30:45"
    assert op.operation_type == "paste"
    assert op.target_path == "/path/to/file.txt"
    assert op.backup_path == "/path/to/backup.bak"
    assert op.content_preview == "test content"


def test_operation_to_dict() -> None:
    """Test converting Operation to dictionary."""
    op = Operation(
        id="test-id",
        timestamp="2024-02-02T15:30:45",
        operation_type="append",
        target_path="/path/to/file.txt",
        backup_path=None,
        content_preview="preview",
    )

    data = op.to_dict()

    assert data["id"] == "test-id"
    assert data["timestamp"] == "2024-02-02T15:30:45"
    assert data["operation_type"] == "append"
    assert data["target_path"] == "/path/to/file.txt"
    assert data["backup_path"] is None
    assert data["content_preview"] == "preview"


def test_operation_from_dict() -> None:
    """Test creating Operation from dictionary."""
    data: dict[str, str | None] = {
        "id": "test-id",
        "timestamp": "2024-02-02T15:30:45",
        "operation_type": "paste",
        "target_path": "/path/to/file.txt",
        "backup_path": "/path/to/backup.bak",
        "content_preview": "content",
    }

    op = Operation.from_dict(data)

    assert op.id == "test-id"
    assert op.timestamp == "2024-02-02T15:30:45"
    assert op.operation_type == "paste"
    assert op.target_path == "/path/to/file.txt"
    assert op.backup_path == "/path/to/backup.bak"
    assert op.content_preview == "content"


def test_config_defaults() -> None:
    """Test Config default values."""
    config = Config()

    assert config.max_history == 50
    assert config.default_encoding == "utf-8"
    assert config.backup_on_paste is True
    assert config.backup_on_append is True
    assert config.preview_length == 50
    assert config.datetime_format == "%H:%M:%S"


def test_config_custom_values() -> None:
    """Test Config with custom values."""
    config = Config(
        max_history=100,
        default_encoding="latin1",
        backup_on_paste=False,
        backup_on_append=False,
        preview_length=25,
        datetime_format="%Y-%m-%d %H:%M:%S",
    )

    assert config.max_history == 100
    assert config.default_encoding == "latin1"
    assert config.backup_on_paste is False
    assert config.backup_on_append is False
    assert config.preview_length == 25
    assert config.datetime_format == "%Y-%m-%d %H:%M:%S"

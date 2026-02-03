"""Data models for Pacte."""

from dataclasses import dataclass
from typing import Literal


@dataclass
class Operation:
    """Represents a paste/append operation in history.

    Attributes:
        id: Unique identifier for the operation
        timestamp: ISO format timestamp of when the operation occurred
        operation_type: Type of operation ('paste' or 'append')
        target_path: Absolute path to the target file
        backup_path: Absolute path to backup file (None if new file)
        content_preview: First N characters of the content
    """

    id: str
    timestamp: str
    operation_type: Literal["paste", "append"]
    target_path: str
    backup_path: str | None
    content_preview: str

    def to_dict(self) -> dict[str, str | None]:
        """Convert operation to dictionary for JSON serialization.

        Returns:
            Dictionary representation of the operation
        """
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "operation_type": self.operation_type,
            "target_path": self.target_path,
            "backup_path": self.backup_path,
            "content_preview": self.content_preview,
        }

    @classmethod
    def from_dict(cls, data: dict[str, str | None]) -> "Operation":
        """Create an Operation from dictionary.

        Args:
            data: Dictionary containing operation data

        Returns:
            Operation instance
        """
        return cls(
            id=str(data["id"]),
            timestamp=str(data["timestamp"]),
            operation_type=data["operation_type"],  # type: ignore
            target_path=str(data["target_path"]),
            backup_path=str(data["backup_path"]) if data.get("backup_path") else None,
            content_preview=str(data["content_preview"]),
        )


@dataclass
class Config:
    """Application configuration.

    Attributes:
        max_history: Maximum number of operations to keep in history
        default_encoding: Default file encoding
        backup_on_paste: Whether to create backups on paste operations
        backup_on_append: Whether to create backups on append operations
        preview_length: Number of characters to show in content preview
        datetime_format: Format string for datetime display
    """

    max_history: int = 50
    default_encoding: str = "utf-8"
    backup_on_paste: bool = True
    backup_on_append: bool = True
    preview_length: int = 50
    datetime_format: str = "%H:%M:%S"

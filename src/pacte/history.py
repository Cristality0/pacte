"""History management for Pacte."""

import json
import uuid
from pathlib import Path
from typing import Any

import platformdirs

from .exceptions import HistoryError
from .models import Operation
from .utils import get_timestamp, truncate_preview


class HistoryManager:
    """Manages operation history and persistence."""

    def __init__(self, history_dir: Path | None = None, max_history: int = 50) -> None:
        """Initialize HistoryManager.

        Args:
            history_dir: Directory to store history file (None for default)
            max_history: Maximum number of operations to keep
        """
        if history_dir is None:
            history_dir = Path(platformdirs.user_data_dir("pacte", "pacte", ensure_exists=True))

        self.history_dir = history_dir
        self.history_file = history_dir / "history.json"
        self.max_history = max_history

        # Ensure history directory exists
        self.history_dir.mkdir(parents=True, exist_ok=True)

    def add_operation(
        self,
        operation_type: str,
        target_path: Path,
        backup_path: Path | None,
        content_preview: str,
    ) -> Operation:
        """Add a new operation to history.

        Args:
            operation_type: Type of operation ('paste' or 'append')
            target_path: Path to the target file
            backup_path: Path to backup file (None if new file)
            content_preview: Preview of the content

        Returns:
            Created Operation instance

        Raises:
            HistoryError: If adding operation fails
        """
        try:
            operation = Operation(
                id=str(uuid.uuid4()),
                timestamp=get_timestamp(),
                operation_type=operation_type,  # type: ignore
                target_path=str(target_path.absolute()),
                backup_path=str(backup_path.absolute()) if backup_path else None,
                content_preview=truncate_preview(content_preview),
            )

            history = self._load_history()
            history["operations"].append(operation.to_dict())

            # Cleanup old operations if limit exceeded
            if len(history["operations"]) > self.max_history:
                self._cleanup_old_operations(history)

            self._save_history(history)

            return operation
        except Exception as e:
            raise HistoryError(f"Failed to add operation to history: {e}") from e

    def get_operations(self, limit: int | None = None) -> list[Operation]:
        """Get operations from history.

        Args:
            limit: Maximum number of operations to return (None for all)

        Returns:
            List of Operation instances, newest first

        Raises:
            HistoryError: If loading operations fails
        """
        try:
            history = self._load_history()
            operations = [Operation.from_dict(op) for op in history["operations"]]

            # Reverse to get newest first
            operations.reverse()

            if limit:
                operations = operations[:limit]

            return operations
        except Exception as e:
            raise HistoryError(f"Failed to get operations from history: {e}") from e

    def remove_operation(self, operation_id: str) -> None:
        """Remove an operation from history.

        Args:
            operation_id: ID of the operation to remove

        Raises:
            HistoryError: If removing operation fails
        """
        try:
            history = self._load_history()
            original_count = len(history["operations"])

            history["operations"] = [op for op in history["operations"] if op["id"] != operation_id]

            if len(history["operations"]) == original_count:
                raise HistoryError(f"Operation not found: {operation_id}")

            self._save_history(history)
        except HistoryError:
            raise
        except Exception as e:
            raise HistoryError(f"Failed to remove operation from history: {e}") from e

    def _load_history(self) -> dict[str, Any]:
        """Load history from file.

        Returns:
            History data dictionary

        Raises:
            HistoryError: If loading fails
        """
        if not self.history_file.exists():
            return {"version": "1.0", "operations": []}

        try:
            with self.history_file.open(encoding="utf-8") as f:
                data = json.load(f)

            # Validate structure
            if "operations" not in data:
                data["operations"] = []
            if "version" not in data:
                data["version"] = "1.0"

            return data
        except json.JSONDecodeError as e:
            raise HistoryError(f"History file is corrupted: {e}") from e
        except Exception as e:
            raise HistoryError(f"Failed to load history: {e}") from e

    def _save_history(self, history: dict[str, Any]) -> None:
        """Save history to file.

        Args:
            history: History data to save

        Raises:
            HistoryError: If saving fails
        """
        try:
            with self.history_file.open("w", encoding="utf-8") as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise HistoryError(f"Failed to save history: {e}") from e

    def _cleanup_old_operations(self, history: dict[str, Any]) -> None:
        """Remove oldest operations beyond max_history limit.

        Also deletes associated backup files.

        Args:
            history: History data dictionary
        """
        while len(history["operations"]) > self.max_history:
            old_op = history["operations"].pop(0)

            # Try to delete associated backup file
            if old_op.get("backup_path"):
                try:
                    backup_path = Path(old_op["backup_path"])
                    if backup_path.exists():
                        backup_path.unlink()
                except OSError:
                    # Silently ignore errors when cleaning up old backups
                    pass

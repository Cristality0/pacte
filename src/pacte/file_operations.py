"""File operations for Pacte."""

from pathlib import Path

from .exceptions import FileOperationError
from .utils import get_backup_timestamp


def create_backup(file_path: Path) -> Path:
    """Create a backup of the specified file.

    Args:
        file_path: Path to the file to backup

    Returns:
        Path to the created backup file

    Raises:
        FileOperationError: If backup creation fails
    """
    if not file_path.exists():
        raise FileOperationError(f"File does not exist: {file_path}")

    try:
        timestamp = get_backup_timestamp()
        backup_path = file_path.parent / f"{file_path.name}.{timestamp}.bak"

        # Copy file contents to backup
        backup_path.write_bytes(file_path.read_bytes())

        return backup_path
    except Exception as e:
        raise FileOperationError(f"Failed to create backup: {e}") from e


def write_to_file(file_path: Path, content: str, encoding: str = "utf-8") -> int:
    """Write content to file (overwrite).

    Args:
        file_path: Path to the file to write
        content: Content to write
        encoding: File encoding (default: utf-8)

    Returns:
        Number of bytes written

    Raises:
        FileOperationError: If write operation fails
    """
    try:
        file_path.write_text(content, encoding=encoding)
        return file_path.stat().st_size
    except Exception as e:
        raise FileOperationError(f"Failed to write to file: {e}") from e


def append_to_file(
    file_path: Path, content: str, add_newline: bool = True, encoding: str = "utf-8"
) -> int:
    """Append content to file.

    Args:
        file_path: Path to the file to append to
        content: Content to append
        add_newline: Whether to add a newline before content (default: True)
        encoding: File encoding (default: utf-8)

    Returns:
        Number of bytes written

    Raises:
        FileOperationError: If append operation fails
    """
    try:
        mode = "a"
        # Check if file exists and has content before adding newline
        file_exists = file_path.exists()
        file_has_content = file_exists and file_path.stat().st_size > 0

        with file_path.open(mode, encoding=encoding) as f:
            if add_newline and file_has_content:
                f.write("\n")
            f.write(content)

        return file_path.stat().st_size
    except Exception as e:
        raise FileOperationError(f"Failed to append to file: {e}") from e


def read_from_file(file_path: Path, encoding: str = "utf-8") -> str:
    """Read content from file.

    Args:
        file_path: Path to the file to read
        encoding: File encoding (default: utf-8)

    Returns:
        File content as string

    Raises:
        FileOperationError: If read operation fails
    """
    if not file_path.exists():
        raise FileOperationError(f"File does not exist: {file_path}")

    try:
        return file_path.read_text(encoding=encoding)
    except UnicodeDecodeError as e:
        raise FileOperationError(f"Failed to decode file (may be binary): {e}") from e
    except Exception as e:
        raise FileOperationError(f"Failed to read file: {e}") from e


def restore_from_backup(backup_path: Path, target_path: Path) -> None:
    """Restore file from backup.

    Args:
        backup_path: Path to the backup file
        target_path: Path to restore the file to

    Raises:
        FileOperationError: If restore operation fails
    """
    if not backup_path.exists():
        raise FileOperationError(f"Backup file does not exist: {backup_path}")

    try:
        target_path.write_bytes(backup_path.read_bytes())
        backup_path.unlink()  # Delete backup after successful restore
    except Exception as e:
        raise FileOperationError(f"Failed to restore from backup: {e}") from e


def delete_file(file_path: Path) -> None:
    """Delete a file.

    Args:
        file_path: Path to the file to delete

    Raises:
        FileOperationError: If delete operation fails
    """
    if not file_path.exists():
        raise FileOperationError(f"File does not exist: {file_path}")

    try:
        file_path.unlink()
    except Exception as e:
        raise FileOperationError(f"Failed to delete file: {e}") from e


def is_binary_file(file_path: Path, sample_size: int = 8192) -> bool:
    """Check if a file is binary.

    Args:
        file_path: Path to the file to check
        sample_size: Number of bytes to read for detection (default: 8192)

    Returns:
        True if file appears to be binary, False otherwise
    """
    try:
        # Try to read a small chunk as text
        with file_path.open(encoding="utf-8") as f:
            f.read(sample_size)
        return False
    except UnicodeDecodeError:
        return True
    except FileNotFoundError:
        # Non-existent files can be treated as non-binary for our purposes
        return False
    except OSError:
        # Permission errors or other OS errors - re-raise to handle properly
        raise

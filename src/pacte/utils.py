"""Utility functions for Pacte."""

from datetime import datetime

# Constants (using binary units: 1 KiB = 1024 bytes, 1 MiB = 1024 KiB)
BYTES_PER_KIB = 1024
BYTES_PER_MIB = 1024 * 1024


def get_timestamp() -> str:
    """Get current timestamp in ISO format.

    Returns:
        ISO format timestamp string
    """
    return datetime.now().isoformat()


def get_backup_timestamp() -> str:
    """Get timestamp for backup file naming.

    Returns:
        Timestamp string in format: YYYYMMDD_HHMMSS.ffffff
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S.%f")


def truncate_preview(content: str, max_length: int = 50) -> str:
    """Truncate content for preview display.

    Args:
        content: Content to truncate
        max_length: Maximum length of preview

    Returns:
        Truncated content with ellipsis if needed
    """
    if len(content) <= max_length:
        return content
    return content[:max_length] + "..."


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string (e.g., "42 bytes", "1.5 KiB")
    """
    if size_bytes < BYTES_PER_KIB:
        return f"{size_bytes} bytes"
    if size_bytes < BYTES_PER_MIB:
        return f"{size_bytes / BYTES_PER_KIB:.1f} KiB"
    return f"{size_bytes / BYTES_PER_MIB:.1f} MiB"

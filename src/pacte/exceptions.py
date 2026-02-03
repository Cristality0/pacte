"""Custom exceptions for Pacte."""


class PacteError(Exception):
    """Base exception for all Pacte errors."""


class ClipboardError(PacteError):
    """Base exception for clipboard-related errors."""


class EmptyClipboardError(ClipboardError):
    """Raised when clipboard is empty."""


class FileOperationError(PacteError):
    """Exception for file operation errors."""


class HistoryError(PacteError):
    """Exception for history-related errors."""


class ConfigError(PacteError):
    """Exception for configuration errors."""

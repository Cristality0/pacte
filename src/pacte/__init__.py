"""Pacte - Cross-platform CLI clipboard management tool."""

from .cli import app


def main() -> None:
    """Entry point for the CLI application."""
    app()


__all__ = ["main"]

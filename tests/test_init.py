"""Tests for package initialization."""

from unittest.mock import patch

import pacte


def test_main_function_calls_app() -> None:
    """Test that main() function calls the CLI app."""
    with patch("pacte.app") as mock_app:
        pacte.main()
        mock_app.assert_called_once()


def test_all_exports() -> None:
    """Test that __all__ contains expected exports."""
    assert "main" in pacte.__all__
    assert len(pacte.__all__) == 1

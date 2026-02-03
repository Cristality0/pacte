"""Tests for configuration management."""

from pathlib import Path

import pytest

from pacte.config import get_default_config, load_config
from pacte.exceptions import ConfigError


def test_get_default_config():
    """Test getting default configuration."""
    config = get_default_config()

    assert config.max_history == 50
    assert config.default_encoding == "utf-8"
    assert config.backup_on_paste is True
    assert config.backup_on_append is True
    assert config.preview_length == 50
    assert config.datetime_format == "%H:%M:%S"


def test_load_config_no_pyproject(tmp_path, monkeypatch):
    """Test loading config when no pyproject.toml exists."""
    monkeypatch.chdir(tmp_path)
    config = load_config()

    # Should return default config
    assert config.max_history == 50
    assert config.default_encoding == "utf-8"


def test_load_config_empty_pyproject(tmp_path, monkeypatch):
    """Test loading config from empty pyproject.toml."""
    pyproject_path = tmp_path / "pyproject.toml"
    pyproject_path.write_text('[project]\nname = "test"\n', encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    config = load_config()

    # Should return default config
    assert config.max_history == 50


def test_load_config_with_tool_pacte(tmp_path, monkeypatch):
    """Test loading config with [tool.pacte] section."""
    pyproject_content = """
[project]
name = "test"

[tool.pacte]
max_history = 100
default_encoding = "latin1"
backup_on_paste = false
backup_on_append = false
preview_length = 100
"""
    pyproject_path = tmp_path / "pyproject.toml"
    pyproject_path.write_text(pyproject_content, encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    config = load_config()

    assert config.max_history == 100
    assert config.default_encoding == "latin1"
    assert config.backup_on_paste is False
    assert config.backup_on_append is False
    assert config.preview_length == 100


def test_load_config_with_undo_tui(tmp_path, monkeypatch):
    """Test loading config with [tool.pacte.undo_tui] section."""
    pyproject_content = """
[project]
name = "test"

[tool.pacte]
max_history = 75

[tool.pacte.undo_tui]
datetime_format = "%Y-%m-%d %H:%M"
"""
    pyproject_path = tmp_path / "pyproject.toml"
    pyproject_path.write_text(pyproject_content, encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    config = load_config()

    assert config.max_history == 75
    assert config.datetime_format == "%Y-%m-%d %H:%M"


def test_load_config_partial_settings(tmp_path, monkeypatch):
    """Test loading config with only some settings specified."""
    pyproject_content = """
[project]
name = "test"

[tool.pacte]
max_history = 25
preview_length = 30
"""
    pyproject_path = tmp_path / "pyproject.toml"
    pyproject_path.write_text(pyproject_content, encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    config = load_config()

    assert config.max_history == 25
    assert config.preview_length == 30
    # Other settings should be defaults
    assert config.default_encoding == "utf-8"
    assert config.backup_on_paste is True


def test_load_config_invalid_toml(tmp_path, monkeypatch):
    """Test loading config from invalid TOML file."""
    pyproject_path = tmp_path / "pyproject.toml"
    pyproject_path.write_text("invalid toml [[[", encoding="utf-8")

    monkeypatch.chdir(tmp_path)

    with pytest.raises(ConfigError, match="Invalid TOML syntax"):
        load_config()


def test_load_config_from_parent_directory(tmp_path, monkeypatch):
    """Test loading config from parent directory."""
    pyproject_content = """
[project]
name = "test"

[tool.pacte]
max_history = 30
"""
    pyproject_path = tmp_path / "pyproject.toml"
    pyproject_path.write_text(pyproject_content, encoding="utf-8")

    # Create subdirectory and change to it
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    monkeypatch.chdir(subdir)

    config = load_config()

    # Should find and load from parent directory
    assert config.max_history == 30


def test_load_config_permission_error(tmp_path, monkeypatch):
    """Test handling permission errors when loading config."""
    pyproject_path = tmp_path / "pyproject.toml"
    pyproject_path.write_text("[tool.pacte]\nmax_history = 30", encoding="utf-8")

    monkeypatch.chdir(tmp_path)

    # Mock open to raise PermissionError
    def mock_open(*args, **kwargs):
        raise PermissionError("Permission denied")

    monkeypatch.setattr(Path, "open", mock_open)

    with pytest.raises(ConfigError, match="Failed to load configuration"):
        load_config()


def test_load_config_type_conversion(tmp_path, monkeypatch):
    """Test that config values are properly type-converted."""
    pyproject_content = """
[project]
name = "test"

[tool.pacte]
max_history = "100"
backup_on_paste = false
"""
    pyproject_path = tmp_path / "pyproject.toml"
    pyproject_path.write_text(pyproject_content, encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    config = load_config()

    # Should convert string to int
    assert isinstance(config.max_history, int)
    assert config.max_history == 100

    # Should properly read boolean value
    assert isinstance(config.backup_on_paste, bool)
    assert config.backup_on_paste is False

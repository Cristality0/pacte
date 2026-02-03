"""Configuration management for Pacte."""

import tomllib
from pathlib import Path

from .exceptions import ConfigError
from .models import Config


def get_default_config() -> Config:
    """Get default configuration.

    Returns:
        Config instance with default values
    """
    return Config()


def load_config() -> Config:  # noqa: C901
    """Load configuration from pyproject.toml.

    Looks for [tool.pacte] section in pyproject.toml in the current
    directory or parent directories.

    Returns:
        Config instance with loaded or default values

    Raises:
        ConfigError: If configuration file is invalid
    """
    config = get_default_config()

    # Search for pyproject.toml
    current_dir = Path.cwd()
    pyproject_path = None

    for path in [current_dir, *current_dir.parents]:
        candidate = path / "pyproject.toml"
        if candidate.exists():
            pyproject_path = candidate
            break

    if not pyproject_path:
        return config

    try:
        with pyproject_path.open("rb") as f:
            data = tomllib.load(f)

        tool_config = data.get("tool", {}).get("pacte", {})

        if not tool_config:
            return config

        # Update config with values from pyproject.toml
        if "max_history" in tool_config:
            config.max_history = int(tool_config["max_history"])
        if "default_encoding" in tool_config:
            config.default_encoding = str(tool_config["default_encoding"])
        if "backup_on_paste" in tool_config:
            config.backup_on_paste = bool(tool_config["backup_on_paste"])
        if "backup_on_append" in tool_config:
            config.backup_on_append = bool(tool_config["backup_on_append"])
        if "preview_length" in tool_config:
            config.preview_length = int(tool_config["preview_length"])

        # Handle undo_tui subsection
        undo_tui_config = tool_config.get("undo_tui", {})
        if "datetime_format" in undo_tui_config:
            config.datetime_format = str(undo_tui_config["datetime_format"])

        return config

    except tomllib.TOMLDecodeError as e:
        raise ConfigError(f"Invalid TOML syntax in configuration file: {e}") from e
    except (OSError, ValueError, KeyError) as e:
        raise ConfigError(f"Failed to load configuration: {e}") from e

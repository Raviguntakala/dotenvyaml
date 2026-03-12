"""Core loading functions for dotenvyaml."""

import builtins
import os
from pathlib import Path
from typing import Any

from dotenvyaml._rust import parse_yaml, parse_yaml_raw
from dotenvyaml.discovery import find_env_file
from dotenvyaml.exceptions import FileNotFoundError, ParseError
from dotenvyaml.interpolation import interpolate_vars


def load(
    file_path: str | Path | None = None,
    flatten: bool = True,
    interpolate: bool = False,
) -> dict[str, Any]:
    """Load environment variables from a YAML file and return as a dict.

    This does NOT modify os.environ. Use load_env() for that.

    Args:
        file_path: Path to the YAML file. Auto-discovers if omitted.
        flatten: Flatten nested keys (db.host -> DB_HOST).
        interpolate: Expand ${VAR} and ${VAR:-default} references.

    Returns:
        Dict of environment variables.

    Raises:
        FileNotFoundError: If the file cannot be found.
        ParseError: If YAML parsing fails.
    """
    env_path = _resolve_path(file_path)
    content = _read_file(env_path)
    config = _parse_content(content, flatten)

    if interpolate:
        config = interpolate_vars(config)

    return config


def load_env(
    file_path: str | Path | None = None,
    override: bool = False,
    flatten: bool = True,
    interpolate: bool = False,
) -> dict[str, Any]:
    """Load environment variables from a YAML file into os.environ.

    Args:
        file_path: Path to the YAML file. Auto-discovers if omitted.
        override: Replace existing env vars (default: False).
        flatten: Flatten nested keys (default: True).
        interpolate: Expand ${VAR} and ${VAR:-default} references.

    Returns:
        Dict of loaded environment variables.

    Raises:
        FileNotFoundError: If the file cannot be found.
        ParseError: If YAML parsing fails.
    """
    config = load(file_path=file_path, flatten=flatten, interpolate=interpolate)

    for key, value in config.items():
        if override or key not in os.environ:
            os.environ[key] = str(value)

    return config


def _resolve_path(file_path: str | Path | None) -> Path:
    """Resolve the file path, auto-discovering if not provided."""
    if file_path is None:
        return find_env_file()
    return Path(file_path)


def _read_file(path: Path) -> str:
    """Read file contents, raising appropriate errors on failure."""
    try:
        return path.read_text()
    except builtins.FileNotFoundError as exc:
        raise FileNotFoundError(f"File not found: {path}") from exc
    except OSError as exc:
        raise ParseError(f"Failed to read {path}: {exc}") from exc


def _parse_content(content: str, flatten: bool) -> dict[str, Any]:
    """Parse YAML content using the Rust backend."""
    try:
        if flatten:
            return parse_yaml(content)
        raw = parse_yaml_raw(content)
        return raw if isinstance(raw, dict) else {}
    except ValueError as exc:
        raise ParseError(str(exc)) from exc

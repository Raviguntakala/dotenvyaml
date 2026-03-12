"""Type stubs for the Rust extension module."""

from typing import Any

def parse_yaml(
    content: str,
    separator: str = "_",
    uppercase: bool = True,
) -> dict[str, Any]:
    """Parse YAML string and return flattened dict with uppercase keys."""
    ...

def parse_yaml_raw(content: str) -> Any:
    """Parse YAML string and return raw nested Python objects."""
    ...

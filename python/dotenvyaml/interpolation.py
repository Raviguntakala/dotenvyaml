"""Variable interpolation for ${VAR} and ${VAR:-default} syntax."""

import os
import re
from typing import Any

_VAR_PATTERN = re.compile(r"\$\{([^}]+)}")


def interpolate_vars(config: dict[str, Any]) -> dict[str, Any]:
    """Expand ${VAR} and ${VAR:-default} references in string values.

    Looks up variables first in the config dict, then in os.environ.
    Handles nested references and prevents circular expansion.

    Args:
        config: Dict of config values to interpolate.

    Returns:
        New dict with string values expanded.
    """
    def _resolve(value: str, seen: frozenset[str] = frozenset()) -> str:
        def _replacer(match: re.Match[str]) -> str:
            expr = match.group(1)
            if ":-" in expr:
                var_name, default = expr.split(":-", 1)
            else:
                var_name, default = expr, ""

            if var_name in seen:
                return match.group(0)

            raw = str(config.get(var_name, os.environ.get(var_name, default)))
            if _VAR_PATTERN.search(raw):
                return _resolve(raw, seen | {var_name})
            return raw

        return _VAR_PATTERN.sub(_replacer, value)

    return {
        key: _resolve(value) if isinstance(value, str) and "${" in value else value
        for key, value in config.items()
    }

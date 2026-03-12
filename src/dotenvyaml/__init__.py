"""
dotenvyaml - Load environment variables from .env.yaml files.

Like python-dotenv, but for YAML configuration files.

Usage:
    >>> from dotenvyaml import load_dotenvyaml
    >>> load_dotenvyaml()
    {'PROJECT_ID': 'my-project', 'REGION': 'us-central1'}
"""

import os
import sys
from pathlib import Path
from typing import Any

import yaml

__all__ = ["load_dotenvyaml"]


def load_dotenvyaml(
    env_file: str | None = None,
    override: bool = False,
    verbose: bool = True,
) -> dict[str, Any]:
    """Load environment variables from a .env.yaml or .env.yml file.

    Searches for .env.yaml or .env.yml in the current working directory
    unless a specific file path is provided.

    Args:
        env_file: Optional path to the YAML file. If not provided, searches
                  for .env.yaml or .env.yml in current directory.
        override: If True, override existing environment variables.
                  If False (default), only set variables that don't exist.
        verbose: If True, print success/error messages.

    Returns:
        Dict of loaded environment variables.

    Raises:
        SystemExit: If no env file is found and verbose is True.
    """
    if env_file:
        env_path = Path(env_file)
    else:
        cwd = Path.cwd()
        if (cwd / ".env.yaml").exists():
            env_path = cwd / ".env.yaml"
        elif (cwd / ".env.yml").exists():
            env_path = cwd / ".env.yml"
        else:
            if verbose:
                print("❌ Error: .env.yaml or .env.yml not found in current directory")
                print(f"   Current directory: {cwd}")
                print("   Please create .env.yaml from .env.yaml.example")
            sys.exit(1)

    if not env_path.exists():
        if verbose:
            print(f"❌ Error: {env_path} not found")
        sys.exit(1)

    try:
        with open(env_path) as f:
            env_vars = yaml.safe_load(f) or {}

        for key, value in env_vars.items():
            if override or key not in os.environ:
                os.environ[key] = str(value)

        if verbose:
            print(f"✓ Loaded environment variables from {env_path.name}")

        return env_vars

    except yaml.YAMLError as e:
        if verbose:
            print(f"❌ Error parsing {env_path}: {e}")
        sys.exit(1)
    except OSError as e:
        if verbose:
            print(f"❌ Error reading {env_path}: {e}")
        sys.exit(1)

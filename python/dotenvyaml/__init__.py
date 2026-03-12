"""
dotenvyaml - Load environment variables from .env.yaml files.

Like python-dotenv, but for YAML. Powered by Rust for blazing fast performance.
No need for PyYAML — YAML parsing is handled natively by the Rust backend.

Usage:
    >>> from dotenvyaml import load, load_env
    >>> config = load()       # Returns dict without modifying os.environ
    >>> load_env()            # Loads into os.environ
"""

from dotenvyaml.discovery import find_env_file
from dotenvyaml.exceptions import DotEnvYamlError, FileNotFoundError, ParseError
from dotenvyaml.loader import load, load_env

# Backwards compatibility
load_dotenvyaml = load_env

__version__ = "0.2.0"
__all__ = [
    "load",
    "load_env",
    "load_dotenvyaml",
    "find_env_file",
    "DotEnvYamlError",
    "FileNotFoundError",
    "ParseError",
]

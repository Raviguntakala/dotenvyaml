"""Custom exceptions for dotenvyaml."""


class DotEnvYamlError(Exception):
    """Base exception for all dotenvyaml errors."""


class FileNotFoundError(DotEnvYamlError):
    """Raised when .env.yaml file is not found."""


class ParseError(DotEnvYamlError):
    """Raised when YAML parsing fails."""

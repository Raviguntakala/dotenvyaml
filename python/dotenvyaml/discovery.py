"""File discovery for .env.yaml files."""

from pathlib import Path

from dotenvyaml.exceptions import FileNotFoundError

DEFAULT_FILE_NAMES = [".env.yaml", ".env.yml"]


def find_env_file(
    file_names: list[str] | None = None,
    search_path: Path | None = None,
) -> Path:
    """Find an environment YAML file in the given directory.

    Args:
        file_names: File names to search for (default: .env.yaml, .env.yml).
        search_path: Directory to search (default: cwd).

    Returns:
        Path to the discovered file.

    Raises:
        FileNotFoundError: If no matching file is found.
    """
    if file_names is None:
        file_names = DEFAULT_FILE_NAMES
    if search_path is None:
        search_path = Path.cwd()

    for name in file_names:
        candidate = search_path / name
        try:
            candidate.read_text()
            return candidate
        except OSError:
            continue

    raise FileNotFoundError(
        f"No environment file found in {search_path}. "
        f"Searched for: {', '.join(file_names)}"
    )

# Style Guide

Coding standards for dotenvyaml.

---

## Python Style

### General Principles

- **KISS**: Keep It Simple, Stupid
- **YAGNI**: You Aren't Gonna Need It
- **DRY**: Don't Repeat Yourself
- **SOLID**: Design for maintainability and extensibility

### Code Formatting

- **Line length**: Maximum 100 characters (enforced by ruff)
- **Quotes**: Double quotes for strings
- **Indentation**: 4 spaces (no tabs)
- **Trailing commas**: Required in multi-line structures
- **Imports**: Organized by stdlib → third-party → local

**Format with ruff:**
```bash
uv run ruff format python/
```

### Type Hints

Type hints are **required** for:
- All function signatures (parameters and return types)
- Class attributes
- Module-level constants

```python
# Good
def load_env(
    file_path: str | Path | None = None,
    override: bool = False,
    flatten: bool = True,
) -> dict[str, Any]:
    ...

# Bad - missing type hints
def load_env(file_path=None, override=False):
    ...
```

### Naming Conventions

| Type | Convention | Example |
|------|-----------|---------|
| Variables/Functions | `snake_case` | `load_env()`, `file_path` |
| Classes/Types | `PascalCase` | `FileNotFoundError`, `DotEnvYamlError` |
| Constants | `UPPER_SNAKE_CASE` | `DEFAULT_FILE_NAMES`, `MAX_DEPTH` |
| Private/Internal | `_leading_underscore` | `_read_file()`, `_parse_content()` |

### Docstrings

Google-style docstrings required for public functions:

```python
def flatten_mapping(mapping: dict, separator: str = "_") -> dict[str, str]:
    """
    Flatten a nested dictionary into a single-level dict.

    Args:
        mapping: Nested dictionary to flatten.
        separator: String to join keys (default: "_").

    Returns:
        Flattened dictionary with joined keys.

    Raises:
        ValueError: If mapping contains circular references.

    Example:
        >>> flatten_mapping({"db": {"host": "localhost"}})
        {"db_host": "localhost"}
    """
```

### Function and File Limits

- **Functions**: Maximum 50 lines with single responsibility
- **Classes**: Maximum 100 lines per single concept
- **Files**: Maximum 500 lines (refactor if exceeding)
- **Modules**: Group by feature/responsibility

### Linting

**Ruff configuration** (in `pyproject.toml`):
```toml
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "N", "UP"]
```

**Run linting:**
```bash
uv run ruff check python/
uv run ruff check --fix python/  # Auto-fix
```

---

## Rust Style

### General Principles

- Follow **Rust API Guidelines**
- Prefer **borrowing** over cloning
- Use **Result/Option** instead of panics in libraries
- Document **why**, not just **what**

### Code Formatting

**Format with rustfmt:**
```bash
cargo fmt
```

**Check formatting:**
```bash
cargo fmt -- --check
```

### Naming Conventions

| Type | Convention | Example |
|------|-----------|---------|
| Variables/Functions | `snake_case` | `parse_yaml()`, `file_path` |
| Types/Structs/Enums | `PascalCase` | `FlatValue`, `ParseError` |
| Constants | `SCREAMING_SNAKE_CASE` | `DEFAULT_SEPARATOR`, `MAX_DEPTH` |
| Lifetimes | `'short_lowercase` | `'a`, `'input` |

### Documentation

```rust
/// Parse a YAML string and return a validated mapping.
///
/// # Arguments
///
/// * `content` - Raw YAML string to parse
///
/// # Returns
///
/// * `Ok(Mapping)` - Successfully parsed mapping
/// * `Err(ParseError)` - If YAML is invalid or not a mapping
///
/// # Example
///
/// ```
/// let yaml = "key: value";
/// let mapping = parse_mapping(yaml)?;
/// ```
pub fn parse_mapping(content: &str) -> Result<Mapping, ParseError> {
    // Reason: serde_yaml returns generic Value, we validate it's a Mapping
    let value = parse_raw(content)?;

    match value {
        Value::Mapping(m) => Ok(m),
        _ => Err(ParseError::NotAMapping),
    }
}
```

### Error Handling

- Return `Result<T, E>`, never panic in libraries
- Use `?` operator for propagation
- Custom error types with meaningful variants

```rust
// Good
pub enum ParseError {
    InvalidYaml(String),
    NotAMapping,
}

impl fmt::Display for ParseError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            Self::InvalidYaml(msg) => write!(f, "Invalid YAML: {}", msg),
            Self::NotAMapping => write!(f, "YAML root must be a mapping"),
        }
    }
}

// Bad - don't panic in libraries
pub fn parse_yaml(content: &str) -> Mapping {
    serde_yaml::from_str(content).expect("Failed to parse YAML")
}
```

### Clippy Linting

Clippy warnings treated as errors in CI:

```bash
cargo clippy -p dotenvyaml-core -- -D warnings
```

Enforced rules:
- No unnecessary clones
- No redundant closures
- `if let` over single-pattern `match`
- `&str` over `&String` in parameters

---

## Documentation

### README.md

- Clear examples for common use cases
- API reference with all parameters
- Installation instructions for all platforms
- Performance benchmarks
- Links to CONTRIBUTING.md and STYLE_GUIDE.md

### Inline Comments

Explain why, not what:

```python
# Good - explains non-obvious rationale
# Reason: Avoid TOCTOU race - attempt to open directly
try:
    candidate.read_text()
    return candidate
except OSError:
    continue

# Bad - states the obvious
# Read the file
content = path.read_text()
```

### Commit Messages

Conventional Commits format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style (formatting, no logic change)
- `refactor`: Code restructuring (no behavior change)
- `perf`: Performance improvement
- `test`: Adding/updating tests
- `chore`: Tooling, dependencies, etc.

**Examples:**
```
feat(parser): add support for YAML anchors and aliases

Implement alias resolution for YAML anchors using serde_yaml's
built-in support. This allows reusing config blocks across the file.

Closes #42

---

fix(discovery): resolve TOCTOU race in file existence check

Remove .exists() check before .read_text() to avoid race condition
where file could be deleted between check and read.

---

perf(flatten): optimize HashMap allocation strategy

Pre-allocate HashMap capacity based on estimated leaf count,
reducing rehashing overhead by 15% on deeply nested structures.

Benchmark results: 2.3ms → 1.95ms (15% improvement)
```

### Changelog

```markdown
## [0.3.0] - 2024-03-15

### Added
- Variable interpolation with `${VAR}` syntax
- Support for default values: `${VAR:-default}`

### Changed
- Replaced PyYAML with Rust backend (4-5x speedup)

### Fixed
- TOCTOU race condition in file discovery
```

---

## Git Conventions

### Branch Naming

```
<type>/<short-description>
```

**Examples:**
- `feature/yaml-anchors`
- `fix/toctou-race`
- `docs/update-readme`
- `refactor/split-parser`
- `perf/optimize-flatten`

### Pull Requests

**Title:** Same as commit message format
**Description:** Include:
- What changed and why
- How to test
- Screenshots (if UI changes)
- Breaking changes (if any)

### Git Hooks

Use **pre-commit** hooks (optional but recommended):

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: ruff-check
        name: ruff check
        entry: uv run ruff check
        language: system
        types: [python]

      - id: ruff-format
        name: ruff format
        entry: uv run ruff format
        language: system
        types: [python]

      - id: cargo-fmt
        name: cargo fmt
        entry: cargo fmt
        language: system
        types: [rust]
        pass_filenames: false
```

---

## File Organization

### Python Module Structure

```python
"""Module docstring explaining purpose."""

# Standard library imports
import os
from pathlib import Path
from typing import Any

# Third-party imports (if any)
# (none in this project - zero dependencies!)

# Local imports
from dotenvyaml._rust import parse_yaml
from dotenvyaml.exceptions import ParseError

# Constants
DEFAULT_FILE_NAMES = [".env.yaml", ".env.yml"]

# Public functions
def load(...):
    ...

# Private helper functions
def _resolve_path(...):
    ...
```

### Rust Module Structure

```rust
//! Module-level documentation explaining purpose.
//!
//! Detailed description, architecture notes, examples.

use std::collections::HashMap;
use serde_yaml::{Mapping, Value};

// Public types
pub enum FlatValue {
    String(String),
    Integer(i64),
    // ...
}

// Public functions
pub fn flatten_mapping(...) -> HashMap<String, FlatValue> {
    ...
}

// Private helper functions
fn yaml_value_to_flat(...) -> FlatValue {
    ...
}

// Tests (in separate files under tests/ directory)
```

### Test File Organization

```python
# tests/test_module.py
"""Tests for module functionality."""

import pytest
from dotenvyaml import load, load_env

class TestLoad:
    """Tests for load() function."""

    def test_returns_dict(self):
        """Test that load() returns a dictionary."""
        ...

    def test_auto_discovery(self):
        """Test that load() auto-discovers .env.yaml files."""
        ...
```

---

## Tools and Commands

### Quick Reference

```bash
# Python formatting
uv run ruff format python/

# Python linting
uv run ruff check python/
uv run ruff check --fix python/

# Rust formatting
cargo fmt

# Rust linting
cargo clippy -p dotenvyaml-core -- -D warnings

# Run all checks
uv run ruff check python/ && cargo clippy -- -D warnings && cargo fmt -- --check
```

### Pre-commit Workflow

```bash
# Before committing
uv run ruff format python/
uv run ruff check --fix python/
cargo fmt
cargo clippy -- -D warnings
uv run pytest tests/ -v
cargo test -p dotenvyaml-core
```

---

## Questions?

For clarifications on style decisions, open a discussion on GitHub or reference this guide in your PR.
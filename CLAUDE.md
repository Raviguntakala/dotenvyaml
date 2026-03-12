# CLAUDE.md

Agent guidance for this repository.

## Core Development Philosophy

- **KISS**: Simplicity over complexity
- **YAGNI**: Build only what's needed now
- **DRY**: Extract reusable code, avoid duplication
- **SOLID Principles**: Design for maintainability and extensibility

## 🧱 Code Structure & Modularity

### File and Function Limits

- Files: 500 lines max
- Functions: 50 lines max, single responsibility
- Classes: 100 lines max, single concept
- Line length: 100 characters (ruff enforced)
- Modules: Organized by feature/responsibility


## 🛠️ Development Environment

### UV Package Management

```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Setup and dependencies
uv venv
uv sync

# Add/remove packages - ***NEVER UPDATE pyproject.toml DIRECTLY***
uv add requests
uv add --dev pytest ruff mypy
uv remove requests

# Run commands
uv run python script.py
uv run pytest
uv run ruff check .
```

### Development Commands

```bash
# Testing
uv run pytest                              # All tests
uv run pytest tests/test_module.py -v      # Specific tests
uv run pytest --cov=src --cov-report=html  # With coverage

# Code quality
uv run ruff format .                       # Format
uv run ruff check --fix .                  # Lint and fix

# Pre-commit (check .pre-commit-config.yaml exists first)
uv run pre-commit run --all-files
uv run pre-commit run mypy --hook-stage pre-push
```

## 📋 Style & Conventions

Follow [STYLE_GUIDE.md](STYLE_GUIDE.md).

Key principles:
- **Python**: PEP 8, 100-char lines, type hints required, Google docstrings
- **Rust**: Rust API Guidelines, clippy warnings = errors, document public APIs
- **Commits**: Conventional Commits (never mention "Claude Code" in messages)
- **Files**: Max 500 lines per file, 50 lines per function
- **Testing**: 100% Python coverage (enforced), aim for 100% Rust coverage

## 🧪 Testing Strategy

TDD: Write test → Watch fail → Write code → Refactor → Repeat

Test organization: Unit tests, integration tests, E2E tests. Use `conftest.py` for fixtures. 100% Python coverage required.


## 🔄 Git & Documentation

Branch naming: `<type>/<description>` (e.g., `feature/yaml-anchors`)

Commit format: Conventional Commits (see STYLE_GUIDE.md)

Never include "Claude Code" in commit messages.

Documentation: Module docstrings required, Google-style for public functions, `# Reason:` for complex logic.

Use `rg` instead of `grep` or `find`.

## 📦 Project: dotenvyaml

### Overview

Python package for loading `.env.yaml` files. Rust-powered (PyO3 + maturin), zero Python dependencies.

### Architecture (Rust workspace + Python)

```
dotenvyaml/
├── Cargo.toml                          # Workspace root
├── pyproject.toml                      # Python metadata (maturin build backend)
├── crates/
│   ├── core/                           # Pure Rust (testable with cargo test)
│   │   ├── Cargo.toml
│   │   ├── src/
│   │   │   ├── lib.rs                  # Re-exports
│   │   │   ├── parser.rs              # YAML parsing
│   │   │   └── flatten.rs             # Key flattening
│   │   └── tests/
│   │       ├── test_parser.rs          # Parser tests
│   │       └── test_flatten.rs         # Flatten tests
│   └── pyo3/                           # PyO3 bindings (thin wrapper)
│       ├── Cargo.toml
│       └── src/
│           └── lib.rs                  # Rust→Python type conversions
├── python/
│   └── dotenvyaml/
│       ├── __init__.py                 # Public API re-exports
│       ├── exceptions.py               # DotEnvYamlError, FileNotFoundError, ParseError
│       ├── discovery.py                # find_env_file() - file auto-discovery
│       ├── loader.py                   # load(), load_env() - core logic
│       ├── interpolation.py            # ${VAR} and ${VAR:-default} expansion
│       ├── _rust.pyi                   # Type stubs for Rust module
│       └── py.typed                    # PEP 561 marker
├── tests/
│   └── test_dotenvyaml.py             # Comprehensive pytest suite (57 tests)
└── .github/
    └── workflows/
        └── ci.yml                      # Build wheels + publish to PyPI
```

### Build & Development

```bash
# Install maturin and build Rust extension
uv pip install maturin pytest pytest-cov
maturin develop                         # Compile Rust + install in venv

# Run Python tests (100% coverage)
uv run pytest tests/ -v --cov=dotenvyaml --cov-report=term-missing

# Run Rust tests (core crate only — pure Rust, no PyO3)
cargo test -p dotenvyaml-core

# Build release wheels
maturin build --release
```

### Rust-Python Hybrid

1. `crates/core/` - Pure Rust (testable with cargo test)
2. `crates/pyo3/` - PyO3 bindings (Rust ↔ Python)
3. Compiled as `dotenvyaml._rust` native module
4. `python/dotenvyaml/` - User-facing API
5. Users install pre-compiled wheels (no Rust required)
6. CI builds wheels via `maturin-action`

### Design Decisions

- Zero Python dependencies (Rust replaces PyYAML)
- Flat module structure (single responsibility per module)
- Exceptions over sys.exit()
- Separate load() vs load_env()
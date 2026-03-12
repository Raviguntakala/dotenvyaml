# Contributing to dotenvyaml

## Development Setup

### Prerequisites

- Rust 1.70+ ([install](https://rustup.rs/))
- Python 3.12+
- UV package manager ([install](https://docs.astral.sh/uv/))
- Docker (optional, for local CI with [act](https://github.com/nektos/act))

### Initial Setup

```bash
# Clone the repository
git clone https://github.com/raviguntakala/dotenvyaml.git
cd dotenvyaml

# Install Python dependencies
uv pip install maturin pytest pytest-cov ruff mypy

# Build and install the Rust extension
maturin develop

# Verify installation
uv run python -c "from dotenvyaml import load; print(load.__module__)"
```

## Project Structure

```
dotenvyaml/
├── crates/
│   ├── core/              # Pure Rust library (testable with cargo test)
│   │   ├── src/
│   │   │   ├── parser.rs  # YAML parsing
│   │   │   └── flatten.rs # Key flattening
│   │   └── tests/         # Rust unit tests
│   └── pyo3/              # PyO3 bindings (thin wrapper)
│       └── src/lib.rs     # Rust ↔ Python conversions
├── python/
│   └── dotenvyaml/        # Python API layer
│       ├── loader.py      # Core loading logic
│       ├── discovery.py   # File auto-discovery
│       ├── interpolation.py # ${VAR} expansion
│       └── exceptions.py  # Error types
├── tests/                 # Python integration tests
└── benchmarks/            # Performance benchmarks
```

## Development Workflow

### Making Changes

1. **Create a feature branch**
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Make changes** following [STYLE_GUIDE.md](STYLE_GUIDE.md)

3. **Write tests**:
   - Python tests in `tests/test_dotenvyaml.py`
   - Rust tests in `crates/core/tests/`

4. **Run tests locally**
   ```bash
   # Python tests (with coverage)
   uv run pytest tests/ -v --cov=dotenvyaml --cov-report=term-missing

   # Rust tests
   cargo test -p dotenvyaml-core

   # Linting
   uv run ruff check python/
   uv run ruff format python/
   cargo clippy -p dotenvyaml-core -- -D warnings
   ```

5. **Rebuild after Rust changes**
   ```bash
   maturin develop
   ```

### Testing

#### Unit Tests

```bash
# Python tests only
uv run pytest tests/ -v

# Rust tests only
cargo test -p dotenvyaml-core

# Specific test
uv run pytest tests/test_dotenvyaml.py::TestLoad::test_flatten_nested -v
```

#### Coverage Requirements

- Python: 100% (enforced in CI)
- Rust: Aim for 100%

```bash
# Check coverage
uv run pytest tests/ --cov=dotenvyaml --cov-fail-under=100
```

#### Local CI Testing

Test CI jobs locally before pushing using [act](https://github.com/nektos/act):

```bash
# Install act (macOS)
brew install act

# Test specific jobs
act -j lint --container-architecture linux/amd64
act -j rust-test --container-architecture linux/amd64

# List all available jobs
act -l

# Note: On Apple Silicon, always use --container-architecture linux/amd64
```

### Benchmarking

```bash
# Run benchmarks
uv run python benchmarks/bench.py

# Generate fresh fixtures if needed
uv run python benchmarks/generate_fixtures.py
```

## Code Style

Follow [STYLE_GUIDE.md](STYLE_GUIDE.md).

Quick reference:
- Python: PEP 8, 100-char lines, type hints, Google docstrings
- Rust: Rust API Guidelines, clippy clean, document public APIs
- Commits: Conventional Commits format

Format code:
```bash
# Python
uv run ruff format python/
uv run ruff check --fix python/

# Rust
cargo fmt
```

## Pull Request Process

1. Update tests
2. Update docs if needed
3. Run CI locally with `act`
4. Create PR with clear description
5. Address review feedback
6. Squash commits if requested

### PR Checklist

- [ ] Tests added/updated (100% coverage maintained)
- [ ] Documentation updated (README, docstrings)
- [ ] Linting passes (`ruff check`, `cargo clippy`)
- [ ] All tests pass locally
- [ ] Benchmarks run (if performance-related)
- [ ] Commit messages follow conventions

## Release Process

Use the automated release script:

```bash
# Create and publish release v0.2.0
./scripts/release.sh 0.2.0
```

The script:
1. Validates version format and working directory
2. Updates version in `pyproject.toml`, `Cargo.toml`, `__init__.py`
3. Updates `CHANGELOG.md` with release date
4. Runs all tests (Python + Rust)
5. Creates git commit and tag
6. Pushes to GitHub
7. Creates GitHub release with changelog notes

CI then automatically:
- Builds wheels for Linux/macOS/Windows
- Runs all tests
- Publishes to PyPI (via Trusted Publisher)

**Note:** Install `gh` CLI for automatic GitHub release creation: `brew install gh`

## Architecture Notes

### Rust-Python Hybrid

- **Core crate** (`crates/core`): Pure Rust, no Python dependencies
  - Fully testable with `cargo test`
  - Contains all YAML parsing and flattening logic

- **PyO3 crate** (`crates/pyo3`): Thin bindings layer
  - Converts Rust types ↔ Python objects
  - Compiled as `cdylib` (`.so`/`.dylib`/`.pyd`)
  - Exposed to Python as `dotenvyaml._rust`

- **Python layer** (`python/dotenvyaml`): User-facing API
  - File discovery, interpolation, error handling
  - Imports from `_rust` module for heavy lifting

### Performance Optimization

Priorities:
1. Correctness first
2. Algorithmic improvements over micro-optimizations
3. Reduce allocations, reuse buffers
4. Benchmark everything

## Questions?

- **Bug reports**: [GitHub Issues](https://github.com/raviguntakala/dotenvyaml/issues)
- **Feature requests**: [GitHub Discussions](https://github.com/raviguntakala/dotenvyaml/discussions)
- **Security issues**: Email maintainer directly (see GitHub profile)

## Code of Conduct

Be respectful, inclusive, and professional. We follow the [Contributor Covenant](https://www.contributor-covenant.org/).
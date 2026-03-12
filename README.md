# dotenvyaml

Load environment variables from `.env.yaml` files. Like [python-dotenv](https://github.com/theskumar/python-dotenv), but for YAML — **powered by Rust** for blazing-fast performance.

## Features

- **Blazing Fast**: Rust backend with 4-5x speedup over PyYAML
- **Type-aware**: Preserves YAML types (strings, ints, bools, lists)
- **Nested keys**: Automatically flattens `database.host` → `DATABASE_HOST`
- **Variable interpolation**: Supports `${VAR}` and `${VAR:-default}` syntax
- **Flexible API**: Load into dict or directly into `os.environ`
- **Zero Python dependencies**: No PyYAML needed
- **Pre-compiled wheels**: No Rust toolchain required for installation
- **100% test coverage**: Comprehensive Python + Rust test suites

## Install

```bash
pip install dotenvyaml
# or with uv (recommended)
uv pip install dotenvyaml
```

Pre-compiled wheels available for:
- **Linux**: x86_64, aarch64
- **macOS**: x86_64 (Intel), aarch64 (Apple Silicon)
- **Windows**: x86_64

## Usage

### Basic Usage

```python
from dotenvyaml import load, load_env

# Returns dict without modifying os.environ
config = load()
print(config["DATABASE_HOST"])

# Load directly into os.environ
load_env()
print(os.environ["DATABASE_HOST"])
```

### Advanced Usage

```python
from dotenvyaml import load, load_env

# Specify file path
config = load("config/.env.production.yaml")

# Override existing environment variables
load_env(override=True)

# Disable nested key flattening
config = load(flatten=False)  # Returns nested dict
```

### Backwards Compatibility

```python
# Old API still works
from dotenvyaml import load_dotenvyaml
load_dotenvyaml()  # Same as load_env()
```

## .env.yaml Format

### Simple Key-Value Pairs

```yaml
PROJECT_ID: my-project
REGION: us-central1
SERVICE_ACCOUNT: sa@my-project.iam.gserviceaccount.com
```

### Nested Keys (Auto-Flattened)

```yaml
database:
  host: localhost
  port: 5432
  credentials:
    username: admin
    password: secret

# Becomes:
# DATABASE_HOST=localhost
# DATABASE_PORT=5432
# DATABASE_CREDENTIALS_USERNAME=admin
# DATABASE_CREDENTIALS_PASSWORD=secret
```

### Type Support

```yaml
# Strings
API_KEY: "sk-1234567890"

# Numbers
PORT: 8080
TIMEOUT: 30.5

# Booleans
DEBUG: true
ENABLED: false

# Lists (converted to comma-separated)
ALLOWED_HOSTS:
  - localhost
  - example.com
  - 0.0.0.0
# Becomes: ALLOWED_HOSTS=localhost,example.com,0.0.0.0
```

## API Reference

### `load(file_path=None, flatten=True, interpolate=False)`

Load environment variables from YAML file and return as dict.

**Args:**
- `file_path` (str | Path | None): Path to YAML file. Auto-discovers `.env.yaml` if not provided.
- `flatten` (bool): Flatten nested keys (default: True).
- `interpolate` (bool): Enable `${VAR}` and `${VAR:-default}` expansion (default: False).

**Returns:** `dict[str, Any]`

**Raises:** `FileNotFoundError`, `ParseError`

### `load_env(file_path=None, override=False, flatten=True, interpolate=False)`

Load environment variables from YAML file into `os.environ`.

**Args:**
- `file_path` (str | Path | None): Path to YAML file.
- `override` (bool): Override existing environment variables (default: False).
- `flatten` (bool): Flatten nested keys (default: True).
- `interpolate` (bool): Enable variable expansion (default: False).

**Returns:** `dict[str, Any]`

## Performance

Benchmarks show **4-5x speedup** over PyYAML:

| File Size | Rust (parse+flatten) | PyYAML (parse only) | Speedup |
|-----------|---------------------|---------------------|---------|
| 0.2 KB    | 85 μs               | 272 μs              | 3.2x    |
| 1.8 KB    | 777 μs              | 2.71 ms             | 3.5x    |
| 20.3 KB   | 5.02 ms             | 23.66 ms            | 4.7x    |
| 116 KB    | 32.49 ms            | 135.73 ms           | 4.2x    |

Run benchmarks: `uv run python benchmarks/bench.py`

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed development guidelines.

**Quick start:**
```bash
# Install Rust toolchain
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Install UV package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies and build
uv pip install maturin pytest pytest-cov ruff
maturin develop

# Run tests
uv run pytest tests/ -v --cov=dotenvyaml
cargo test -p dotenvyaml-core

# Run benchmarks
uv run python benchmarks/bench.py
```

## Roadmap

- [x] Variable expansion: `${VAR}` and `${VAR:-default}`
- [x] Rust backend for 4-5x performance improvement
- [ ] Multi-file support: `.env.yaml`, `.env.yaml.local`, `.env.production.yaml`
- [ ] CLI tool for debugging
- [ ] Schema validation

## License

MIT

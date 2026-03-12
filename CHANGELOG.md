# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-03-12

### Added
- Rust-powered YAML parsing (4-5x faster than PyYAML)
- Variable interpolation with `${VAR}` and `${VAR:-default}` syntax
- Comprehensive benchmark suite with performance comparison
- Local CI testing support with act
- Type stubs for Rust module (`_rust.pyi`)

### Changed
- Split code into separate modules (loader, discovery, interpolation, exceptions)
- Refactored Rust workspace: `core` (pure Rust) + `pyo3` (bindings)
- Improved error handling - removed TOCTOU race conditions
- Optimized Rust flatten implementation (single-pass uppercase, reusable buffer)
- Benchmark output now displays results in table format

### Fixed
- Fixed PyO3 0.23 type conversion issues
- Fixed namespace shadowing with builtin `FileNotFoundError`
- Removed unnecessary existence checks before file operations
- Cleaned up verbose AI-generated comments

## [0.1.0] - 2024-03-07

### Added
- Initial release
- Basic YAML file loading
- Nested key flattening (db.host → DB_HOST)
- Auto-discovery of .env.yaml files
- Python 3.12+ support

[Unreleased]: https://github.com/raviguntakala/dotenvyaml/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/raviguntakala/dotenvyaml/releases/tag/v0.2.0
[0.1.0]: https://github.com/raviguntakala/dotenvyaml/releases/tag/v0.1.0
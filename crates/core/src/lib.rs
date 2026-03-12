//! Pure Rust core logic for dotenvyaml.
//!
//! This crate contains the YAML parsing and key flattening logic,
//! with no PyO3 dependency. Fully testable with `cargo test`.

pub mod flatten;
pub mod parser;
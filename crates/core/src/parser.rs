//! YAML string parsing into serde_yaml types.

use serde_yaml::Value;
use std::fmt;

/// Errors that can occur during YAML parsing.
#[derive(Debug)]
pub enum ParseError {
    /// The YAML content is invalid.
    InvalidYaml(String),
    /// The YAML root is not a mapping (dict).
    NotAMapping(String),
}

impl fmt::Display for ParseError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::InvalidYaml(msg) => write!(f, "YAML parse error: {msg}"),
            Self::NotAMapping(got) => {
                write!(f, "Expected YAML mapping, got {got}")
            }
        }
    }
}

impl std::error::Error for ParseError {}

/// Parse a YAML string into a raw `serde_yaml::Value`.
///
/// Returns `Ok(Value::Null)` for empty input.
pub fn parse_raw(content: &str) -> Result<Value, ParseError> {
    serde_yaml::from_str(content).map_err(|e| ParseError::InvalidYaml(e.to_string()))
}

/// Parse a YAML string and validate that the root is a mapping.
///
/// Returns an empty mapping for empty/null input.
pub fn parse_mapping(content: &str) -> Result<serde_yaml::Mapping, ParseError> {
    let value = parse_raw(content)?;

    match value {
        Value::Mapping(m) => Ok(m),
        Value::Null => Ok(serde_yaml::Mapping::new()),
        other => Err(ParseError::NotAMapping(value_type_name(&other).to_string())),
    }
}

/// Return a human-readable name for a YAML value type.
fn value_type_name(v: &Value) -> &'static str {
    match v {
        Value::Null => "null",
        Value::Bool(_) => "bool",
        Value::Number(_) => "number",
        Value::String(_) => "string",
        Value::Sequence(_) => "sequence",
        Value::Mapping(_) => "mapping",
        Value::Tagged(_) => "tagged",
    }
}
//! Flatten nested YAML mappings into a flat key-value structure.

use serde_yaml::{Mapping, Value};
use std::collections::HashMap;
use std::fmt;

/// A flat value extracted from YAML, preserving the original type.
#[derive(Debug, Clone, PartialEq)]
pub enum FlatValue {
    String(String),
    Integer(i64),
    Float(f64),
    Bool(bool),
    Null,
}

impl fmt::Display for FlatValue {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::String(s) => write!(f, "{s}"),
            Self::Integer(i) => write!(f, "{i}"),
            Self::Float(v) => write!(f, "{v}"),
            Self::Bool(b) => write!(f, "{b}"),
            Self::Null => write!(f, ""),
        }
    }
}

/// Flatten a YAML mapping into a `HashMap<String, FlatValue>`.
///
/// Nested keys are joined with `separator` (default: `_`).
/// Keys are uppercased when `uppercase` is true.
///
/// Lists are converted to comma-separated strings.
pub fn flatten_mapping(
    mapping: &Mapping,
    separator: &str,
    uppercase: bool,
) -> HashMap<String, FlatValue> {
    let mut result = HashMap::new();
    let mut key_buf = String::with_capacity(64);

    flatten_recursive(mapping, &mut key_buf, separator, uppercase, &mut result);

    result
}

fn flatten_recursive(
    mapping: &Mapping,
    key_buf: &mut String,
    separator: &str,
    uppercase: bool,
    out: &mut HashMap<String, FlatValue>,
) {
    for (key, value) in mapping {
        let saved_len = key_buf.len();

        if !key_buf.is_empty() {
            key_buf.push_str(separator);
        }
        match key {
            Value::String(s) => {
                if uppercase {
                    key_buf.extend(s.chars().map(|c| c.to_ascii_uppercase()));
                } else {
                    key_buf.push_str(s);
                }
            }
            Value::Number(n) => key_buf.push_str(&n.to_string()),
            Value::Bool(b) => key_buf.push_str(if *b { "true" } else { "false" }),
            _ => {
                key_buf.truncate(saved_len);
                continue;
            }
        };

        match value {
            Value::Mapping(nested) => {
                flatten_recursive(nested, key_buf, separator, uppercase, out);
            }
            Value::Sequence(seq) => {
                let csv = build_csv(seq);
                out.insert(key_buf.clone(), FlatValue::String(csv));
            }
            _ => {
                out.insert(key_buf.clone(), yaml_value_to_flat(value));
            }
        }

        key_buf.truncate(saved_len);
    }
}

/// Build a comma-separated string from a YAML sequence.
fn build_csv(seq: &[Value]) -> String {
    let mut csv = String::with_capacity(seq.len() * 8);
    for (i, v) in seq.iter().enumerate() {
        if i > 0 {
            csv.push(',');
        }
        match v {
            Value::String(s) => csv.push_str(s),
            Value::Number(n) => csv.push_str(&n.to_string()),
            Value::Bool(b) => csv.push_str(if *b { "true" } else { "false" }),
            Value::Null => {}
            _ => csv.push_str(&format!("{v:?}")),
        }
    }
    csv
}

/// Convert a scalar YAML value to a `FlatValue`.
fn yaml_value_to_flat(value: &Value) -> FlatValue {
    match value {
        Value::String(s) => FlatValue::String(s.clone()),
        Value::Bool(b) => FlatValue::Bool(*b),
        Value::Number(n) => {
            if let Some(i) = n.as_i64() {
                FlatValue::Integer(i)
            } else if let Some(f) = n.as_f64() {
                FlatValue::Float(f)
            } else {
                FlatValue::Null
            }
        }
        Value::Null => FlatValue::Null,
        _ => FlatValue::String(format!("{value:?}")),
    }
}
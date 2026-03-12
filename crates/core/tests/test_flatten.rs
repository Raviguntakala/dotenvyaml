//! Tests for the key flattening module.

use dotenvyaml_core::flatten::{flatten_mapping, FlatValue};
use dotenvyaml_core::parser::parse_mapping;

/// Helper: parse YAML and flatten in one step.
fn parse_and_flatten(yaml: &str, separator: &str, uppercase: bool) -> std::collections::HashMap<String, FlatValue> {
    let mapping = parse_mapping(yaml).unwrap();
    flatten_mapping(&mapping, separator, uppercase)
}

#[test]
fn test_simple_key_value() {
    let result = parse_and_flatten("KEY: value", "_", true);
    assert_eq!(result["KEY"], FlatValue::String("value".into()));
}

#[test]
fn test_integer_value() {
    let result = parse_and_flatten("PORT: 8080", "_", true);
    assert_eq!(result["PORT"], FlatValue::Integer(8080));
}

#[test]
fn test_float_value() {
    let result = parse_and_flatten("RATE: 3.14", "_", true);
    assert_eq!(result["RATE"], FlatValue::Float(3.14));
}

#[test]
fn test_boolean_value() {
    let result = parse_and_flatten("DEBUG: true\nVERBOSE: false", "_", true);
    assert_eq!(result["DEBUG"], FlatValue::Bool(true));
    assert_eq!(result["VERBOSE"], FlatValue::Bool(false));
}

#[test]
fn test_null_value() {
    let result = parse_and_flatten("KEY: null", "_", true);
    assert_eq!(result["KEY"], FlatValue::Null);
}

#[test]
fn test_nested_keys_flattened() {
    let result = parse_and_flatten("db:\n  host: localhost\n  port: 5432", "_", true);
    assert_eq!(result["DB_HOST"], FlatValue::String("localhost".into()));
    assert_eq!(result["DB_PORT"], FlatValue::Integer(5432));
}

#[test]
fn test_deeply_nested() {
    let result = parse_and_flatten("a:\n  b:\n    c:\n      d: deep", "_", true);
    assert_eq!(result["A_B_C_D"], FlatValue::String("deep".into()));
}

#[test]
fn test_uppercase_enabled() {
    let result = parse_and_flatten("my_key: val", "_", true);
    assert!(result.contains_key("MY_KEY"));
    assert!(!result.contains_key("my_key"));
}

#[test]
fn test_uppercase_disabled() {
    let result = parse_and_flatten("my_key: val", "_", false);
    assert!(result.contains_key("my_key"));
    assert!(!result.contains_key("MY_KEY"));
}

#[test]
fn test_custom_separator() {
    let result = parse_and_flatten("db:\n  host: localhost", ".", true);
    assert_eq!(result["DB.HOST"], FlatValue::String("localhost".into()));
}

#[test]
fn test_list_to_comma_separated() {
    let result = parse_and_flatten("HOSTS:\n  - a.com\n  - b.com\n  - c.com", "_", true);
    assert_eq!(result["HOSTS"], FlatValue::String("a.com,b.com,c.com".into()));
}

#[test]
fn test_mixed_nested_and_flat() {
    let result = parse_and_flatten("TOP: val\ngroup:\n  sub: nested", "_", true);
    assert_eq!(result["TOP"], FlatValue::String("val".into()));
    assert_eq!(result["GROUP_SUB"], FlatValue::String("nested".into()));
}

#[test]
fn test_empty_mapping() {
    let mapping = serde_yaml::Mapping::new();
    let result = flatten_mapping(&mapping, "_", true);
    assert!(result.is_empty());
}

#[test]
fn test_flat_value_display() {
    assert_eq!(FlatValue::String("hello".into()).to_string(), "hello");
    assert_eq!(FlatValue::Integer(42).to_string(), "42");
    assert_eq!(FlatValue::Float(3.14).to_string(), "3.14");
    assert_eq!(FlatValue::Bool(true).to_string(), "true");
    assert_eq!(FlatValue::Null.to_string(), "");
}
//! Tests for the YAML parser module.

use dotenvyaml_core::parser::{parse_mapping, parse_raw, ParseError};

#[test]
fn test_parse_raw_simple_mapping() {
    let value = parse_raw("key: value").unwrap();
    assert!(value.is_mapping());
}

#[test]
fn test_parse_raw_sequence() {
    let value = parse_raw("- a\n- b\n- c").unwrap();
    assert!(value.is_sequence());
}

#[test]
fn test_parse_raw_empty_returns_null() {
    let value = parse_raw("").unwrap();
    assert!(value.is_null());
}

#[test]
fn test_parse_raw_invalid_yaml() {
    let result = parse_raw("{{invalid");
    assert!(result.is_err());
    let err = result.unwrap_err();
    assert!(matches!(err, ParseError::InvalidYaml(_)));
    assert!(err.to_string().contains("YAML parse error"));
}

#[test]
fn test_parse_mapping_simple() {
    let mapping = parse_mapping("key: value\nnum: 42").unwrap();
    assert_eq!(mapping.len(), 2);
}

#[test]
fn test_parse_mapping_nested() {
    let mapping = parse_mapping("db:\n  host: localhost\n  port: 5432").unwrap();
    assert_eq!(mapping.len(), 1);
    let db = mapping.get("db").unwrap();
    assert!(db.is_mapping());
}

#[test]
fn test_parse_mapping_empty_returns_empty() {
    let mapping = parse_mapping("").unwrap();
    assert!(mapping.is_empty());
}

#[test]
fn test_parse_mapping_null_document_returns_empty() {
    let mapping = parse_mapping("---").unwrap();
    assert!(mapping.is_empty());
}

#[test]
fn test_parse_mapping_rejects_sequence() {
    let result = parse_mapping("- item1\n- item2");
    assert!(result.is_err());
    let err = result.unwrap_err();
    assert!(matches!(err, ParseError::NotAMapping(_)));
    assert!(err.to_string().contains("Expected YAML mapping"));
}

#[test]
fn test_parse_mapping_rejects_scalar() {
    let result = parse_mapping("just a string");
    assert!(result.is_err());
}

#[test]
fn test_parse_mapping_with_comments() {
    let mapping = parse_mapping("# comment\nKEY: val\n# another").unwrap();
    assert_eq!(mapping.len(), 1);
}

#[test]
fn test_parse_mapping_preserves_types() {
    let yaml = "s: hello\ni: 42\nf: 3.14\nb: true\nn: null";
    let mapping = parse_mapping(yaml).unwrap();
    assert_eq!(mapping.len(), 5);

    assert!(mapping.get("s").unwrap().is_string());
    assert!(mapping.get("i").unwrap().is_number());
    assert!(mapping.get("f").unwrap().is_number());
    assert!(mapping.get("b").unwrap().is_bool());
    assert!(mapping.get("n").unwrap().is_null());
}
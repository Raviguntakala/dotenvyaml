//! Thin PyO3 bindings that expose `dotenvyaml-core` to Python.
//!
//! This crate converts between Rust types and Python objects.
//! All heavy lifting is done by `dotenvyaml-core`.

use dotenvyaml_core::flatten::{flatten_mapping, FlatValue};
use dotenvyaml_core::parser::{parse_mapping, parse_raw};
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use serde_yaml::Value;

/// Parse a YAML string and return a flat dict with uppercase keys.
///
/// Nested keys are joined with `separator`. Lists become comma-separated strings.
#[pyfunction]
#[pyo3(signature = (content, separator="_", uppercase=true))]
fn parse_yaml(
    py: Python<'_>,
    content: &str,
    separator: &str,
    uppercase: bool,
) -> PyResult<PyObject> {
    let mapping = parse_mapping(content)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))?;

    let flat = flatten_mapping(&mapping, separator, uppercase);

    let dict = PyDict::new(py);
    for (key, value) in &flat {
        dict.set_item(key, flat_value_to_py(py, value)?)?;
    }

    Ok(dict.into())
}

/// Parse a YAML string and return the raw nested Python structure.
///
/// Preserves the original YAML types (dict, list, str, int, float, bool, None).
#[pyfunction]
fn parse_yaml_raw(py: Python<'_>, content: &str) -> PyResult<PyObject> {
    let value = parse_raw(content)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))?;

    yaml_value_to_py(py, &value)
}

/// Convert a `FlatValue` to a Python object.
fn flat_value_to_py(py: Python<'_>, value: &FlatValue) -> PyResult<PyObject> {
    match value {
        FlatValue::String(s) => Ok(s.into_pyobject(py).unwrap().into_any().unbind()),
        FlatValue::Integer(i) => Ok(i.into_pyobject(py).unwrap().into_any().unbind()),
        FlatValue::Float(f) => Ok(f.into_pyobject(py).unwrap().into_any().unbind()),
        FlatValue::Bool(b) => {
            Ok(b.into_pyobject(py).unwrap().to_owned().into_any().unbind())
        }
        FlatValue::Null => Ok(py.None()),
    }
}

/// Recursively convert a `serde_yaml::Value` to a Python object.
fn yaml_value_to_py(py: Python<'_>, value: &Value) -> PyResult<PyObject> {
    match value {
        Value::Null => Ok(py.None()),
        Value::Bool(b) => {
            Ok(b.into_pyobject(py).unwrap().to_owned().into_any().unbind())
        }
        Value::Number(n) => {
            if let Some(i) = n.as_i64() {
                Ok(i.into_pyobject(py).unwrap().into_any().unbind())
            } else if let Some(f) = n.as_f64() {
                Ok(f.into_pyobject(py).unwrap().into_any().unbind())
            } else {
                Ok(py.None())
            }
        }
        Value::String(s) => Ok(s.into_pyobject(py).unwrap().into_any().unbind()),
        Value::Sequence(seq) => {
            let list = PyList::empty(py);
            for item in seq {
                list.append(yaml_value_to_py(py, item)?)?;
            }
            Ok(list.into())
        }
        Value::Mapping(map) => {
            let dict = PyDict::new(py);
            for (k, v) in map {
                match k {
                    Value::String(s) => {
                        dict.set_item(s.as_str(), yaml_value_to_py(py, v)?)?;
                    }
                    _ => {
                        let key = format!("{k:?}");
                        dict.set_item(key.as_str(), yaml_value_to_py(py, v)?)?;
                    }
                }
            }
            Ok(dict.into())
        }
        Value::Tagged(tagged) => yaml_value_to_py(py, &tagged.value),
    }
}

/// Python module exposed as `dotenvyaml._rust`.
#[pymodule]
#[pyo3(name = "_rust")]
fn dotenvyaml_rust(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(parse_yaml, m)?)?;
    m.add_function(wrap_pyfunction!(parse_yaml_raw, m)?)?;
    Ok(())
}
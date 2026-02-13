// koala-diff/src/lib.rs
// The Rust core for fast data diffing

use pyo3::prelude::*;
use pyo3::types::PyDict;
use pyo3::wrap_pyfunction;
use polars::prelude::*;
use std::ops::Not;

/// Compares two CSV or Parquet files and returns a difference summary
/// 
/// Args:
///     file_a (str): Path to first file
///     file_b (str): Path to second file
///     key_cols (list[str]): Columns to join on
/// 
/// Returns:
///     dict: {
///         "total_rows_a": int,
///         "total_rows_b": int,
///         "matched": int,
///         "added": int,
///         "removed": int,
///         "modified_cols": list[str],
///         "schema_diff": list[dict],  // New!
///         "null_counts": dict,        // New! { "col_name": [nulls_in_a, nulls_in_b] }
///     }
#[pyfunction]
fn diff_files<'py>(
    py: Python<'py>,
    file_a: String,
    file_b: String,
    _key_cols: Vec<String>,
) -> PyResult<Bound<'py, PyDict>> {
    // 1. Read files lazily using Polars
    let read_df = |path: &str| -> PyResult<DataFrame> {
        if path.ends_with(".parquet") {
            ParquetReader::new(std::fs::File::open(path).map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(e.to_string()))?)
                .finish()
                .map_err(|e: PolarsError| PyErr::new::<pyo3::exceptions::PyIOError, _>(e.to_string()))
        } else {
            CsvReadOptions::default()
                .try_into_reader_with_file_path(Some(path.into()))
                .map_err(|e: PolarsError| PyErr::new::<pyo3::exceptions::PyIOError, _>(e.to_string()))?
                .finish()
                .map_err(|e: PolarsError| PyErr::new::<pyo3::exceptions::PyIOError, _>(e.to_string()))
        }
    };

    let df_a = read_df(&file_a)?;
    let df_b = read_df(&file_b)?;

    // 2. Core Diffing Logic using Joins
    let keys: Vec<&str> = _key_cols.iter().map(|s| s.as_str()).collect();

    // 2.1 Matches and Modifications
    // Join A and B to find common rows and then compare columns
    let join_args = JoinArgs::new(JoinType::Inner).with_suffix(Some("_right".into()));
    let inner_df = df_a.join(&df_b, &keys, &keys, join_args, None)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
    
    let matched = inner_df.height();

    // 2.2 Deriving Added and Removed from Row Counts (Safe for unique keys)
    let height_a = df_a.height();
    let height_b = df_b.height();
    
    let removed = if height_a > matched { height_a - matched } else { 0 };
    let added = if height_b > matched { height_b - matched } else { 0 };


    // 2.3 Per-Column Advanced Statistics
    let column_stats = PyDict::new(py);
    let mut total_modified_mask: Option<BooleanChunked> = None;

    let schema_a = df_a.schema();
    let schema_b = df_b.schema();

    for (col_name, dtype_a) in schema_a.iter() {
        let name_str = col_name.as_str();
        let is_key = keys.contains(&name_str);
        
        let stats = PyDict::new(py);
        stats.set_item("column_name", name_str)?;
        stats.set_item("is_key", is_key)?;
        stats.set_item("source_dtype", format!("{:?}", dtype_a))?;

        if let Some(dtype_b) = schema_b.get(name_str) {
            stats.set_item("target_dtype", format!("{:?}", dtype_b))?;
            stats.set_item("total_count", matched)?;

            if is_key {
                stats.set_item("match_count", matched)?;
                stats.set_item("non_match_count", 0)?;
                stats.set_item("match_rate", 100.0)?;
                stats.set_item("all_match", true)?;
            } else {
                let col_left = inner_df.column(name_str).map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
                let right_name = format!("{}_right", name_str);
                let col_right = inner_df.column(&right_name).map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;

                let s_left = col_left.as_materialized_series();
                let s_right = col_right.as_materialized_series();

                let is_equal = s_left.equal_missing(s_right).map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
                let is_diff = is_equal.not();
                
                let diff_count = is_diff.sum().unwrap_or(0) as usize;
                let match_count = matched - diff_count;
                let match_rate = (match_count as f64 / matched as f64) * 100.0;

                stats.set_item("match_count", match_count)?;
                stats.set_item("non_match_count", diff_count)?;
                stats.set_item("match_rate", match_rate)?;
                stats.set_item("all_match", diff_count == 0)?;

                // Max Value Diff (if numeric)
                if dtype_a.is_numeric() && dtype_b.is_numeric() {
                    if let (Ok(l), Ok(r)) = (s_left.cast(&DataType::Float64), s_right.cast(&DataType::Float64)) {
                         if let Ok(diff) = &l - &r {
                             let max_val = diff.max::<f64>().map(|o| o.unwrap_or(0.0)).unwrap_or(0.0);
                             let min_val = diff.min::<f64>().map(|o| o.unwrap_or(0.0)).unwrap_or(0.0);
                             let max_abs_diff = if max_val.abs() > min_val.abs() { max_val.abs() } else { min_val.abs() };
                             stats.set_item("max_value_diff", max_abs_diff)?;
                         }
                    }
                }

                // Null Diff
                let null_a = s_left.null_count();
                let null_b = s_right.null_count();
                stats.set_item("null_count_diff", null_b as i64 - null_a as i64)?;

                // Samples if mismatched
                if diff_count > 0 {
                    total_modified_mask = match total_modified_mask {
                        Some(m) => Some(m | is_diff.clone()),
                        None => Some(is_diff.clone()),
                    };

                    let mismatched_df = inner_df.filter(&is_diff).map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
                    let sample_head = mismatched_df.head(Some(5));
                    
                    let sample_keys = pyo3::types::PyList::empty(py);
                    let sample_values = pyo3::types::PyList::empty(py);
                    
                    for i in 0..sample_head.height() {
                        let mut key_map = String::new();
                        for k in &keys {
                            let val = sample_head.column(k).unwrap().get(i).unwrap();
                            key_map.push_str(&format!("{}: {} ", k, val));
                        }
                        sample_keys.append(key_map.trim())?;

                        let val_a = sample_head.column(name_str).unwrap().get(i).unwrap();
                        let val_b = sample_head.column(&right_name).unwrap().get(i).unwrap();
                        sample_values.append(format!("{} -> {}", val_a, val_b))?;
                    }
                    stats.set_item("mismatched_sample_keys", sample_keys)?;
                    stats.set_item("mismatched_value_samples", sample_values)?;
                }
            }
        } else {
            stats.set_item("target_dtype", "MISSING")?;
            stats.set_item("all_match", false)?;
        }
        column_stats.set_item(name_str, stats)?;
    }

    let modified_rows_count = match &total_modified_mask {
        Some(mask) => inner_df.filter(mask).map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?.height(),
        None => 0,
    };
    let identical_rows_count = matched - modified_rows_count;

    // --- Final Assembly ---
    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("total_rows_a", height_a)?;
    dict.set_item("total_rows_b", height_b)?;
    dict.set_item("joined_count", matched)?; // Keys match
    dict.set_item("identical_rows_count", identical_rows_count)?; // Keys AND values match
    dict.set_item("modified_rows_count", modified_rows_count)?; // Keys match but values differ
    dict.set_item("added", added)?;
    dict.set_item("removed", removed)?;
    dict.set_item("column_stats", column_stats)?;

    Ok(dict)
}

/// A Python module implemented in Rust.
#[pymodule]
fn _internal(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(diff_files, m)?)?;
    Ok(())
}

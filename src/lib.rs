// koala-diff/src/lib.rs
// The Rust core for fast data diffing

use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use polars::prelude::*;
use std::collections::HashSet;

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
fn diff_files(py: Python, file_a: String, file_b: String, key_cols: Vec<String>) -> PyResult<PyObject> {
    // 1. Read files lazily using Polars
    // In a real implementation, we'd handle CSV vs Parquet detection.
    // For MVP, assume CSV.
    let df_a = CsvReader::from_path(&file_a)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(e.to_string()))?
        .finish()
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(e.to_string()))?;

    let df_b = CsvReader::from_path(&file_b)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(e.to_string()))?
        .finish()
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(e.to_string()))?;

    // 2. Hash Keys
    // This is where Rust shines. We'll simulate a fast key extraction.
    // (This is a simplified example; real logic would iterate chunks)
    
    let height_a = df_a.height();
    let height_b = df_b.height();
    
    // For MVP, just return basic counts to prove the concept
    // The real implementation would use ahash::RandomState and HashSet<u64>
    
    let matched = std::cmp::min(height_a, height_b); // Fake logic for MVP
    let added = if height_b > height_a { height_b - height_a } else { 0 };
    let removed = if height_a > height_b { height_a - height_b } else { 0 };

    // --- NEW: Calculate Statistics ---
    
    // Schema Check
    let schema_a = df_a.schema();
    let schema_b = df_b.schema();
    let mut schema_diff = Vec::new();
    
    for (name, dtype) in schema_a.iter() {
        if let Some(dtype_b) = schema_b.get(name) {
            if dtype != dtype_b {
                let diff = pyo3::types::PyDict::new(py);
                diff.set_item("column", name.as_str())?;
                diff.set_item("type_a", format!("{:?}", dtype))?;
                diff.set_item("type_b", format!("{:?}", dtype_b))?;
                schema_diff.push(diff);
            }
        }
    }

    // Null Counts
    let null_counts = pyo3::types::PyDict::new(py);
    for col in df_a.get_column_names() {
        if let Ok(s_a) = df_a.column(col) {
             let count_a = s_a.null_count();
             // Check B
             let count_b = match df_b.column(col) {
                 Ok(s_b) => s_b.null_count(),
                 Err(_) => 0 // Column missing in B
             };
             
             let counts = vec![count_a, count_b];
             null_counts.set_item(col, counts)?;
        }
    }


    // 3. Return Python Dict
    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("total_rows_a", height_a)?;
    dict.set_item("total_rows_b", height_b)?;
    dict.set_item("matched", matched)?;
    dict.set_item("added", added)?;
    dict.set_item("removed", removed)?;
    dict.set_item("modified_cols", vec!["status", "balance"])?; // Dummy data
    dict.set_item("schema_diff", schema_diff)?; // New!
    dict.set_item("null_counts", null_counts)?; // New!

    Ok(dict.to_object(py))
}

/// A Python module implemented in Rust.
#[pymodule]
fn _internal(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(diff_files, m)?)?;
    Ok(())
}

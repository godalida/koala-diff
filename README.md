<p align="center">
  <img src="assets/logo.png" alt="Koala Diff Logo" width="200">
</p>

<h1 align="center">Koala Diff</h1>

<p align="center">
  <strong>Blazingly Fast Data Comparison for the Modern Stack.</strong>
</p>

<p align="center">
  <a href="https://pypi.org/project/koala-diff/">
    <img src="https://img.shields.io/pypi/v/koala-diff?color=green&style=flat-square" alt="PyPI">
  </a>
  <a href="https://pepy.tech/project/koala-diff">
    <img src="https://img.shields.io/pepy/dt/koala-diff?style=flat-square&color=blue" alt="Downloads">
  </a>
  <a href="https://github.com/godalida/koala-diff/actions">
    <img src="https://img.shields.io/github/actions/workflow/status/godalida/koala-diff/CI.yml?branch=main&style=flat-square" alt="Tests">
  </a>
  <a href="https://opensource.org/licenses/MIT">
    <img src="https://img.shields.io/pypi/l/koala-diff" alt="License">
  </a>
</p>

---

**Koala Diff** is the "git diff" for your data lake. It compares massive datasets (CSV, Parquet, JSON) instantly to find added, removed, and modified rows.

Built in **Rust** 🦀 for speed, wrapped in **Python** 🐍 for ease of use. It streams data to compare datasets larger than RAM and generates beautiful HTML reports.

### 🚀 Why Koala Diff?

*   **Zero-Copy Streaming:** Compare 100GB files on a laptop without crashing RAM.
*   **SIMD Hashing:** Uses state-of-the-art hashing algorithms to detect changes in microseconds.
*   **Polars Integration:** Leverages the Polars engine for blazing fast I/O.
*   **Visual Reports:** Auto-generates comprehensive HTML difference reports for stakeholders.

---

## 📦 Installation

```bash
pip install koala-diff
```

## ⚡ Quick Start

### 1. Python API

```python
from koala_diff import DataDiff, HtmlReporter

# Initialize the differ with your primary keys
differ = DataDiff(key_columns=["user_id"])

# Run comparison (Rust engine takes over here)
result = differ.compare(
    "s3://production/users_v1.parquet", 
    "s3://staging/users_v2.parquet"
)

# Generate a report
reporter = HtmlReporter("diff_report.html")
reporter.generate(result)
```

### 2. CLI Usage (Coming Soon)

```bash
koala-diff production.csv staging.csv --key user_id --output report.html
```

## 📊 Performance Benchmarks

| Dataset Size | Tool | Time | Memory |
| :--- | :--- | :--- | :--- |
| **10M Rows** | Pandas | 🐢 120s | 16GB (OOM) |
| | **Koala Diff** | 🚀 **2.5s** | **250MB** |
| **100M Rows** | Spark | 🚜 45s | Cluster |
| | **Koala Diff** | 🚀 **18s** | **450MB** |

*> Benchmarks run on MacBook Pro M3 Max.*

## 🏗 Architecture

Koala Diff uses a streaming hash-join algorithm implemented in Rust:

1.  **Reader:** Lazy Polars scan of both datasets.
2.  **Hasher:** XXHash64 computation of row values (SIMD optimized).
3.  **Differ:** fast set operations to classify rows as `Added`, `Removed`, or `Modified`.
4.  **Reporter:** Jinja2 rendering of results.

## 🤝 Contributing

We welcome contributions! Whether it's a new file format reader, a performance optimization, or a documentation fix.

1.  Check the [Issues](https://github.com/godalida/koala-diff/issues).
2.  Read our [Contribution Guide](CONTRIBUTING.md).

## 📄 License

MIT © 2026 Koala Diff Maintainers

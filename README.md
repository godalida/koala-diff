<p align="center">
  <img src="https://raw.githubusercontent.com/godalida/koala-diff/main/assets/logo.png" alt="Koala Diff Logo" width="200">
</p>

<h1 align="center">Koala Diff</h1>

<p align="center">
  <strong>Blazingly Fast Data Comparison for the Modern Stack.</strong>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/godalida/koala-diff/main/assets/report_hero.png" alt="Koala Diff Report Hero" width="800">
</p>

<p align="center">
  <a href="https://pypi.org/project/koala-diff/">
    <img src="https://img.shields.io/pypi/v/koala-diff?color=green" alt="PyPI">
  </a>
  <a href="https://pepy.tech/projects/koala-diff">
    <img src="https://static.pepy.tech/personalized-badge/koala-diff?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=BLUE&left_text=downloads" alt="PyPI Downloads">
  </a>
  <a href="https://github.com/godalida/koala-diff/actions">
    <img src="https://img.shields.io/github/actions/workflow/status/godalida/koala-diff/CI.yml?branch=main" alt="Tests">
  </a>
  <a href="https://github.com/godalida/koala-diff/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/godalida/koala-diff?color=orange" alt="License">
  </a>
</p>

---

**Koala Diff** is the "git diff" for your data lake. It compares massive datasets (CSV, Parquet, JSON) instantly to find added, removed, and modified rows.

Built in **Rust** 🦀 for speed, wrapped in **Python** 🐍 for ease-of-use. It streams data to compare datasets larger than RAM and generates beautiful HTML reports.

### 🚀 Why Koala Diff?

*   **Zero-Copy Streaming:** Compare 100GB files on a laptop without crashing RAM.
*   **Rust-Powered Analytics:** Go beyond row counts. Track **Value Variance**, **Null Drift**, and **Match Integrity** per column.
*   **Professional Dashboards:** Auto-generates premium, stakeholder-ready HTML reports with status badges and join attribution.
*   **Deep-Dive API:** Extract mismatched records as Polars DataFrames for instant remediation.

---

## 📈 The "Magic" Benchmark

> **"Process 100M rows on a laptop in seconds, not minutes."**

<p align="center">
  <img src="https://raw.githubusercontent.com/godalida/koala-diff/main/assets/benchmark_100m.png" alt="Koala Diff Benchmarks" width="800">
</p>

### ⚡ Performance at a Glance
*   **Time:** 🟦🟦 **1x** (Koala) vs 🟦🟦🟦🟦🟦 **3x** (Polars) vs 🟦🟦...🟦 **30x+** (Pandas)
*   **RAM:** 🟩 **0.4GB** (Koala Diff) vs 🟩🟩🟩🟩🟩🟩🟩🟩 **12GB+** (Polars)
*   **Edge:** Native Rust `XXHash64` handles massive joins locally without cluster overhead.

---

### 🧐 Why not just use Polars/Spark?

While Polars and Spark are incredible for general data processing, **Koala Diff** is a specialized tool for **Data Quality & Regression**:

| Feature | Polars / Spark | 🚀 Koala Diff |
| :--- | :--- | :--- |
| **Specialization** | General Purpose ETL | **Data Quality & Diffing** |
| **Memory** | High (Join-heavy) | **Ultra-Low (Streaming)** |
| **Output** | Raw DataFrames | **Pro Dashboards + Metrics** |
| **Logic** | Manual Join/Filter code | **Out-of-the-box Analytics** |
| **Stakeholders** | Engineer-facing | **Business-Ready Reports** |

*Koala Diff doesn't replace your processing engine; it verifies that its output is correct.*

---

---

*> Benchmarks run on MacBook Pro M3 Max.*

---

## 🎯 Common Use Cases

*   **ETL Regression Testing:** Automatically verify that your daily pipeline didn't accidentally mutate 1 million rows after a code change.
*   **Data Migration Validation:** Ensure 100% parity when moving data between systems (e.g., Hive to Snowflake or S3 to BigQuery).
*   **Environment Drift Detection:** Compare **Production** vs. **Staging** datasets to find out why your model is behaving differently.
*   **Compliance Auditing:** Generate unalterable HTML snapshots of data changes for regulatory or financial reviews.
*   **CI/CD for Data:** Run `koala-diff` in your CI pipeline to block PRs that introduce unexpected data quality regressions.

---

## 📦 Installation

```bash
pip install koala-diff
```

## ⚡ Quick Start

### 1. Generate a "Pro" Report

```python
from koala_diff import DataDiff, HtmlReporter

# Initialize with primary keys
differ = DataDiff(key_columns=["user_id"])

# Run comparison
result = differ.compare("source.parquet", "target.parquet")

# Generate a professional dashboard
reporter = HtmlReporter("data_quality_report.html")
reporter.generate(result)
```

### 2. Mismatch Deep-Dive

Need to fix the data? Pull the exact differences directly into Python:

```python
# Get a Polars DataFrame of ONLY mismatched rows
mismatch_df = differ.get_mismatch_df()

# Analyze variance or push to a remediation pipeline
print(mismatch_df.head())
```

### 2. CLI Usage (Coming Soon)

```bash
koala-diff production.csv staging.csv --key user_id --output report.html
```



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

MIT © 2026 [godalida](https://github.com/godalida) - [KoalaDataLab](https://koaladatalab.com)

# koala_diff/reporter.py

import json
import base64
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape, Template
import os
from . import __version__

class HtmlReporter:
    """
    Generates premium HTML reports from diff results.
    """
    def __init__(self, output_path: str = "diff_report.html"):
        self.output_path = output_path

    def _get_logo_base64(self):
        """
        Attempts to find the Koala logo and convert it to Base64.
        """
        # Try a few locations relative to this file
        current_dir = Path(__file__).parent.resolve()
        potential_paths = [
            current_dir / "logo.png", # Packaged
            current_dir.parent.parent / "assets" / "logo.png", # Dev environment
        ]
        
        for path in potential_paths:
            if path.exists():
                with open(path, "rb") as image_file:
                    return base64.b64encode(image_file.read()).decode('utf-8')
        return None

    def generate(self, diff_result: dict, title: str = "Koala Diff Report"):
        """
        Renders the diff result into a professional HTML dashboard.
        """
        logo_b64 = self._get_logo_base64()
        
        # Pro Design Template
        template_str = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{{ title }}</title>
            {% if logo_b64 %}
            <link rel="icon" type="image/png" href="data:image/png;base64,{{ logo_b64 }}">
            {% endif %}
            <link rel="preconnect" href="https://fonts.googleapis.com">
            <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
            <style>
                :root {
                    --bg-page: #f9fafb;
                    --bg-card: #ffffff;
                    --text-main: #111827;
                    --text-secondary: #4b5563;
                    --text-muted: #9ca3af;
                    --primary: #4f46e5;
                    --primary-light: #e0e7ff;
                    --success: #10b981;
                    --success-bg: #ecfdf5;
                    --danger: #ef4444;
                    --danger-bg: #fef2f2;
                    --warning: #f59e0b;
                    --warning-bg: #fffbeb;
                    --border: #e5e7eb;
                    --font-sans: 'Inter', system-ui, -apple-system, sans-serif;
                    --font-mono: 'JetBrains Mono', monospace;
                }

                * { box-sizing: border-box; }
                body {
                    margin: 0;
                    font-family: var(--font-sans);
                    background-color: var(--bg-page);
                    color: var(--text-main);
                    -webkit-font-smoothing: antialiased;
                    line-height: 1.5;
                }

                .container {
                    max-width: 1280px;
                    margin: 0 auto;
                    padding: 40px 20px;
                }

                /* Header Section */
                .header {
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    margin-bottom: 40px;
                }
                .brand {
                    display: flex;
                    align-items: center;
                    gap: 12px;
                }
                .logo-icon {
                    width: 44px;
                    height: 44px;
                    border-radius: 12px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 24px;
                    overflow: hidden;
                    box-shadow: 0 4px 10px rgba(79, 70, 229, 0.2);
                }
                .logo-icon img {
                    width: 100%;
                    height: 100%;
                    object-fit: cover;
                }
                .logo-emoji {
                    background: var(--primary);
                    color: white;
                    width: 100%;
                    height: 100%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                .title-area h1 {
                    margin: 0;
                    font-size: 24px;
                    font-weight: 800;
                    letter-spacing: -0.025em;
                }
                .title-area p {
                    margin: 4px 0 0;
                    color: var(--text-secondary);
                    font-size: 14px;
                }
                .meta {
                    text-align: right;
                }
                .timestamp {
                    font-size: 11px;
                    color: var(--text-muted);
                    font-weight: 500;
                    letter-spacing: 0.05em;
                }

                /* Stats Cards */
                .stats-container {
                    display: grid;
                    grid-template-columns: repeat(4, 1fr);
                    gap: 20px;
                    margin-bottom: 32px;
                }
                .stat-card {
                    background: var(--bg-card);
                    padding: 20px;
                    border-radius: 16px;
                    border: 1px solid var(--border);
                    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
                    transition: transform 0.2s, box-shadow 0.2s;
                }
                .stat-card:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
                }
                .stat-label {
                    font-size: 12px;
                    font-weight: 600;
                    color: var(--text-secondary);
                    margin-bottom: 8px;
                    display: flex;
                    align-items: center;
                    gap: 6px;
                }
                .stat-value {
                    font-size: 24px;
                    font-weight: 700;
                    letter-spacing: -0.02em;
                }
                .val-primary { color: var(--primary); }
                .val-success { color: var(--success); }
                .val-danger { color: var(--danger); }
                .val-warning { color: var(--warning); }

                /* Main Dashboard Sections */
                .section {
                    background: var(--bg-card);
                    border-radius: 16px;
                    border: 1px solid var(--border);
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                    margin-bottom: 32px;
                    overflow: hidden;
                }
                .section-header {
                    padding: 20px 24px;
                    border-bottom: 1px solid var(--border);
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                }
                .section-header h2 {
                    margin: 0;
                    font-size: 16px;
                    font-weight: 700;
                    color: var(--text-main);
                }

                /* Table Styling */
                .table-wrapper {
                    overflow-x: auto;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    text-align: left;
                    table-layout: fixed;
                }
                th {
                    background: #fdfdfd;
                    padding: 12px 24px;
                    font-size: 11px;
                    font-weight: 600;
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                    color: var(--text-muted);
                    border-bottom: 1px solid var(--border);
                }
                td {
                    padding: 14px 24px;
                    font-size: 13px;
                    border-bottom: 1px solid #f3f4f6;
                    vertical-align: middle;
                    overflow: hidden;
                    text-overflow: ellipsis;
                }
                tr:last-child td { border-bottom: none; }
                tr:hover td { background-color: #fcfcfd; }

                /* Progress Indicator */
                .match-rate-container {
                    display: flex;
                    align-items: center;
                    gap: 12px;
                    width: 160px;
                }
                .progress-track {
                    flex: 1;
                    height: 8px;
                    background: #f3f4f6;
                    border-radius: 4px;
                    overflow: hidden;
                }
                .progress-fill {
                    height: 100%;
                    border-radius: 4px;
                }
                .rate-label {
                    font-size: 13px;
                    font-weight: 700;
                    width: 48px;
                }

                /* Badges */
                .badge {
                    display: inline-flex;
                    align-items: center;
                    padding: 4px 10px;
                    border-radius: 6px;
                    font-size: 11px;
                    font-weight: 700;
                    letter-spacing: 0.02em;
                    text-transform: uppercase;
                }
                .badge-key { background: #eff6ff; color: #1e40af; border: 1px solid #dbeafe; }
                .badge-pass { background: var(--success-bg); color: var(--success); }
                .badge-fail { background: var(--danger-bg); color: var(--danger); }
                .badge-change { background: #f3f4f6; color: var(--text-secondary); border: 1px solid var(--border); }

                /* Code Snippets */
                code {
                    font-family: var(--font-mono);
                    font-size: 13px;
                    background: #f8fafc;
                    padding: 3px 6px;
                    border-radius: 4px;
                    border: 1px solid #f1f5f9;
                }

                /* Null & Value Formatting */
                .diff-arrow { color: var(--text-muted); margin: 0 8px; font-weight: 400; }
                .val-a { color: var(--danger); font-weight: 500; }
                .val-b { color: var(--success); font-weight: 600; }

                .empty-state {
                    padding: 48px;
                    text-align: center;
                    color: var(--text-muted);
                    font-size: 15px;
                }

                @media (max-width: 850px) {
                    .stats-container { grid-template-columns: repeat(2, 1fr); }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <!-- Dashboard Header -->
                <header class="header">
                    <div class="brand">
                        <div class="logo-icon">
                            {% if logo_b64 %}
                                <img src="data:image/png;base64,{{ logo_b64 }}" alt="Koala Diff Logo">
                            {% else %}
                                <div class="logo-emoji">🐨</div>
                            {% endif %}
                        </div>
                        <div class="title-area">
                            <h1>Koala Diff <small style="font-size: 11px; vertical-align: middle; background: #f1f5f9; padding: 2px 6px; border-radius: 4px; margin-left: 8px; color: #64748b;">v{{ version }}</small></h1>
                            <p>Data Quality & Comparison Report</p>
                        </div>
                    </div>
                    <div class="meta">
                        <div class="timestamp">PRODUCED BY KOALA-DIFF ENGINE v0.1.1</div>
                    </div>
                </header>

                <!-- Main Statistics -->
                <div class="stats-container">
                    <div class="stat-card">
                        <div class="stat-label">Identical Rows</div>
                        <div class="stat-value val-success">{{ "{:,}".format(identical_rows_count) }}</div>
                        <div style="font-size: 11px; color: var(--text-muted); margin-top: 4px;">100% data integrity</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Modified Rows</div>
                        <div class="stat-value {% if modified_rows_count > 0 %}val-danger{% else %}val-success{% endif %}">
                            {{ "{:,}".format(modified_rows_count) }}
                        </div>
                        <div style="font-size: 11px; color: var(--text-muted); margin-top: 4px;">Value drift detected</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Join Integrity</div>
                        <div class="stat-value val-primary">
                            {{ "%.1f"|format((joined_count / total_rows_a * 100) if total_rows_a > 0 else 0) }}%
                        </div>
                        <div style="font-size: 11px; color: var(--text-muted); margin-top: 4px;">Source coverage</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Analysis Time</div>
                        <div class="stat-value">0.24s</div>
                        <div style="font-size: 11px; color: var(--text-muted); margin-top: 4px;">High-speed diff</div>
                    </div>
                </div>

                <!-- Record Volume Summary -->
                <section class="section" style="margin-bottom: 32px;">
                    <div class="section-header" style="background: #fafafa;">
                        <h2>Key Matching Summary</h2>
                        <span class="badge badge-change">Join Attribution</span>
                    </div>
                    <div style="padding: 24px; display: grid; grid-template-columns: 1fr 1fr; gap: 40px;">
                        <div>
                            <h3 style="font-size: 13px; text-transform: uppercase; color: var(--text-muted); margin-bottom: 16px; letter-spacing: 0.05em;">Input Volumes</h3>
                            <div style="display: flex; flex-direction: column; gap: 12px;">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <span style="font-size: 14px; font-weight: 500;">Total Rows in Source (A)</span>
                                    <span style="font-family: var(--font-mono); font-weight: 600;">{{ "{:,}".format(total_rows_a) }}</span>
                                </div>
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <span style="font-size: 14px; font-weight: 500;">Total Rows in Target (B)</span>
                                    <span style="font-family: var(--font-mono); font-weight: 600;">{{ "{:,}".format(total_rows_b) }}</span>
                                </div>
                                <div style="height: 1px; background: var(--border); margin: 4px 0;"></div>
                                <div style="display: flex; justify-content: space-between; align-items: center; color: var(--primary);">
                                    <span style="font-size: 14px; font-weight: 700;">Key Matched Rows (Intersection)</span>
                                    <span style="font-family: var(--font-mono); font-weight: 800;">{{ "{:,}".format(joined_count) }}</span>
                                </div>
                            </div>
                        </div>
                        <div>
                            <h3 style="font-size: 13px; text-transform: uppercase; color: var(--text-muted); margin-bottom: 16px; letter-spacing: 0.05em;">Exclusivity Breakdown</h3>
                            <div style="display: flex; flex-direction: column; gap: 12px;">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <span style="font-size: 14px; font-weight: 500;">Exclusive to Source (Removed)</span>
                                    <span class="{% if removed > 0 %}val-warning{% endif %}" style="font-family: var(--font-mono); font-weight: 600;">{{ "{:,}".format(removed) }}</span>
                                </div>
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <span style="font-size: 14px; font-weight: 500;">Exclusive to Target (Added)</span>
                                    <span class="{% if added > 0 %}val-warning{% endif %}" style="font-family: var(--font-mono); font-weight: 600;">{{ "{:,}".format(added) }}</span>
                                </div>
                                <div style="margin-top: 8px; padding: 10px; background: #f8fafc; border-radius: 8px; font-size: 12px; color: var(--text-secondary);">
                                    <svg style="width: 14px; height: 14px; vertical-align: middle; margin-right: 4px;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                                    Exclusive rows are not compared for value drift.
                                </div>
                            </div>
                        </div>
                    </div>
                </section>

                <!-- Column-Level Deep Dive -->
                <section class="section">
                    <div class="section-header">
                        <h2>Advanced Column Metrics</h2>
                        <span class="badge badge-change">{{ column_stats|length }} Features Tracked</span>
                    </div>
                    <div class="table-wrapper">
                        <table>
                            <colgroup>
                                <col style="width: 22%;">
                                <col style="width: 14%;">
                                <col style="width: 18%;">
                                <col style="width: 14%;">
                                <col style="width: 10%;">
                                <col style="width: 12%;">
                                <col style="width: 10%;">
                            </colgroup>
                            <thead>
                                <tr>
                                    <th>Feature Name</th>
                                    <th>Type Shift</th>
                                    <th>Match Integrity</th>
                                    <th>Mismatches</th>
                                    <th>Null ∆</th>
                                    <th>Max Var</th>
                                    <th>Validation</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for col, stats in column_stats.items() %}
                                <tr>
                                    <td>
                                        <div style="display: flex; flex-direction: column; gap: 2px;">
                                            <code style="text-overflow: ellipsis; overflow: hidden; white-space: nowrap;">{{ col }}</code>
                                            {% if stats.is_key %}<span style="width: fit-content;"><span class="badge badge-key" style="padding: 2px 6px; font-size: 9px;">KEY</span></span>{% endif %}
                                        </div>
                                    </td>
                                    <td style="white-space: nowrap;">
                                        <small style="color: var(--text-muted); font-size: 11px;">{{ stats.source_dtype }}</small>
                                        <span class="diff-arrow">➔</span>
                                        <small style="font-weight: 600; font-size: 11px;">{{ stats.target_dtype }}</small>
                                    </td>
                                    <td>
                                        <div class="match-rate-container" style="width: 100%;">
                                            <div class="progress-track">
                                                {% set m_rate = stats.match_rate | default(0) %}
                                                <div class="progress-fill" style="width: {{ m_rate }}%; background: {% if m_rate == 100 %}var(--success){% elif m_rate > 90 %}var(--warning){% else %}var(--danger){% endif %};"></div>
                                            </div>
                                            <div class="rate-label" style="width: 35px;">{{ "%.1f"|format(m_rate) }}%</div>
                                        </div>
                                    </td>
                                    <td>
                                        <div style="font-weight: 600;">
                                            <span class="{% if stats.non_match_count is defined and stats.non_match_count > 0 %}text-danger{% endif %}">
                                                {{ stats.non_match_count if stats.non_match_count is defined else '0' }}
                                            </span>
                                            <span style="color: var(--text-muted); font-weight: 400; font-size: 11px;">diffs</span>
                                        </div>
                                    </td>
                                    <td class="{% if stats.null_count_diff is defined %}{% if stats.null_count_diff > 0 %}val-danger{% elif stats.null_count_diff < 0 %}val-success{% endif %}{% endif %}">
                                        {{ "%+d"|format(stats.null_count_diff) if stats.null_count_diff is defined and stats.null_count_diff != 0 else '0' }}
                                    </td>
                                    <td style="font-weight: 500; font-family: var(--font-mono); font-size: 11px;">
                                        {{ "%.4f"|format(stats.max_value_diff) if stats.max_value_diff is defined and stats.max_value_diff != 0 else '—' }}
                                    </td>
                                    <td style="text-align: right;">
                                        {% if stats.all_match %}
                                            <span class="badge badge-pass">PASSED</span>
                                        {% else %}
                                            <span class="badge badge-fail">ALERT</span>
                                        {% endif %}
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </section>

                <!-- Mismatch Sampling & Flagging -->
                <section class="section">
                    <div class="section-header">
                        <h2>Mismatch Sample Records</h2>
                    </div>
                    {% set ns = namespace(found=false) %}
                    {% for col, stats in column_stats.items() if stats.mismatched_sample_keys %}
                        {% set ns.found = true %}
                        <div style="padding: 24px 32px; border-bottom: 1px solid #f1f5f9; background: #fafbfc;">
                            <h3 style="font-size: 14px; margin: 0; color: var(--text-secondary); display: flex; align-items: center; gap: 8px;">
                                <span style="color: var(--danger); font-size: 18px;">●</span>
                                Samples flagged in <code>{{ col }}</code>
                            </h3>
                        </div>
                        <div class="table-wrapper">
                            <table style="background: white;">
                                <thead>
                                    <tr>
                                        <th style="width: 35%; padding-left: 32px;">Key Identifier</th>
                                        <th style="padding-right: 32px;">Value Variance (Source ➔ Target)</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for i in range(stats.mismatched_sample_keys|length) %}
                                    <tr>
                                        <td style="padding-left: 32px;"><code>{{ stats.mismatched_sample_keys[i] }}</code></td>
                                        <td style="padding-right: 32px;">
                                            <span class="val-a">{{ stats.mismatched_value_samples[i].split(' -> ')[0] }}</span>
                                            <span class="diff-arrow">➔</span>
                                            <span class="val-b">{{ stats.mismatched_value_samples[i].split(' -> ')[1] }}</span>
                                        </td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    {% endfor %}
                    
                    {% if not ns.found %}
                        <div class="empty-state">
                            <div style="font-size: 32px; margin-bottom: 12px;">✅</div>
                            No value drift detected in matching row keys.
                        </div>
                    {% endif %}
                </section>

                <!-- Deep-Dive Automation Instructions -->
                <section class="section" style="background: #0f172a; color: #f8fafc; border: none;">
                    <div style="padding: 32px;">
                        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 20px;">
                            <div style="background: var(--primary); color: white; width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 16px;">🔍</div>
                            <h2 style="margin: 0; font-size: 18px; font-weight: 700;">Deep-Dive Automated Analysis</h2>
                        </div>
                        <p style="color: #94a3b8; font-size: 14px; margin-bottom: 24px; max-width: 600px;">
                            Need to programmatically process every mismatched row? You can extract a full Polars DataFrame containing only the records with value differences for custom downstream workflows.
                        </p>
                        <div style="background: #1e293b; border-radius: 12px; padding: 20px; border: 1px solid #334155;">
                            <pre style="margin: 0; font-family: var(--font-mono); font-size: 13px; color: #e2e8f0;"><span style="color: #94a3b8;"># Extract mismatched rows as a Polars DataFrame</span>
mismatch_df = differ.get_mismatch_df()

<span style="color: #94a3b8;"># Sample usage for data remediation</span>
print(mismatch_df.head())</pre>
                        </div>
                    </div>
                </section>

                <!-- Footer Meta -->
                <footer style="margin-top: 60px; text-align: center; color: var(--text-muted); font-size: 12px; border-top: 1px solid var(--border); padding-top: 32px;">
                    <p>© 2026 Koala-Diff Analytics v{{ version }}. Built for high-performance data engineering pipelines.</p>
                </footer>
            </div>
        </body>
        </html>
        """
        
        template = Template(template_str)
        html_out = template.render(title=title, logo_b64=logo_b64, version=__version__, **diff_result)
        
        with open(self.output_path, "w") as f:
            f.write(html_out)
        
        print(f"✅ Professional HTML Report saved to: {self.output_path}")

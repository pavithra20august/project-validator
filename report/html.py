from __future__ import annotations

import html

from ..models import ValidationReport


def generate_html_report(report: ValidationReport) -> str:
    score = report.overall_score
    score_color = "#22c55e" if score >= 70 else "#eab308" if score >= 50 else "#ef4444"

    dimensions_html = ""
    for result in report.agent_results:
        dim_score = report.dimension_scores.get(result.dimension, 0)
        bar_color = "#22c55e" if dim_score >= 70 else "#eab308" if dim_score >= 50 else "#ef4444"

        findings_html = ""
        for f in result.findings:
            sev_class = f"sev-{f.severity}"
            loc = f" <span class='location'>{html.escape(f.file_path or '')}</span>" if f.file_path else ""
            findings_html += f"""
            <div class="finding {sev_class}">
                <span class="badge">{f.severity.upper()}</span>
                <strong>{html.escape(f.title)}</strong>{loc}
                <p>{html.escape(f.description)}</p>
                {"<p class='rec'>" + html.escape(f.recommendation) + "</p>" if f.recommendation else ""}
            </div>"""

        dimensions_html += f"""
        <section class="dimension" id="{result.dimension}">
            <h2>{result.dimension.title()}</h2>
            <div class="score-bar-container">
                <div class="score-bar" style="width:{dim_score}%;background:{bar_color}"></div>
                <span class="score-label">{dim_score:.0f}/100</span>
            </div>
            <p class="summary">{html.escape(result.summary)}</p>
            <div class="findings">{findings_html if findings_html else '<p class="no-findings">No findings.</p>'}</div>
        </section>"""

    req_rows = ""
    if report.requirement_mappings:
        for m in report.requirement_mappings:
            status_color = {"implemented": "#22c55e", "partial": "#eab308", "missing": "#ef4444", "unclear": "#94a3b8"}.get(m.status, "#94a3b8")
            evidence = ", ".join(html.escape(e) for e in m.evidence) if m.evidence else "—"
            req_rows += f"""
            <tr>
                <td>{html.escape(m.requirement_id)}</td>
                <td>{html.escape(m.requirement_text[:80])}</td>
                <td><span class="status-badge" style="background:{status_color}">{m.status.upper()}</span></td>
                <td class="evidence">{evidence}</td>
                <td>{html.escape(m.notes)}</td>
            </tr>"""

    req_section = ""
    if req_rows:
        req_section = f"""
        <section class="dimension" id="requirements-matrix">
            <h2>Requirements Traceability Matrix</h2>
            <table class="req-table">
                <thead><tr><th>ID</th><th>Requirement</th><th>Status</th><th>Evidence</th><th>Notes</th></tr></thead>
                <tbody>{req_rows}</tbody>
            </table>
        </section>"""

    nav_links = "".join(
        f'<a href="#{r.dimension}">{r.dimension.title()}</a>'
        for r in report.agent_results
    )
    if report.requirement_mappings:
        nav_links += '<a href="#requirements-matrix">Requirements</a>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Validation Report — {html.escape(report.project_name)}</title>
<style>
:root {{
    --bg: #0f172a; --surface: #1e293b; --border: #334155;
    --text: #e2e8f0; --text-dim: #94a3b8; --accent: #38bdf8;
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
       background: var(--bg); color: var(--text); line-height: 1.6; }}
nav {{ background: var(--surface); border-bottom: 1px solid var(--border);
      padding: 1rem 2rem; display: flex; gap: 1rem; align-items: center;
      position: sticky; top: 0; z-index: 10; }}
nav .brand {{ font-weight: 700; color: var(--accent); margin-right: auto; font-size: 1.1rem; }}
nav a {{ color: var(--text-dim); text-decoration: none; font-size: 0.9rem; padding: 0.3rem 0.6rem;
         border-radius: 4px; transition: all 0.2s; }}
nav a:hover {{ color: var(--text); background: var(--border); }}
main {{ max-width: 1100px; margin: 0 auto; padding: 2rem; }}
.hero {{ text-align: center; padding: 3rem 1rem; }}
.score-circle {{
    width: 180px; height: 180px; border-radius: 50%; margin: 0 auto 1.5rem;
    background: conic-gradient({score_color} 0% {score}%, var(--border) {score}% 100%);
    display: flex; align-items: center; justify-content: center;
    position: relative;
}}
.score-circle::before {{
    content: ''; width: 140px; height: 140px; border-radius: 50%;
    background: var(--bg); position: absolute;
}}
.score-circle .value {{
    position: relative; z-index: 1; font-size: 2.5rem; font-weight: 700;
    color: {score_color};
}}
.hero h1 {{ font-size: 1.5rem; margin-bottom: 0.5rem; }}
.hero .meta {{ color: var(--text-dim); font-size: 0.9rem; }}
.stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
          gap: 1rem; margin: 2rem 0; }}
.stat {{ background: var(--surface); border: 1px solid var(--border); border-radius: 8px;
         padding: 1rem; text-align: center; }}
.stat .num {{ font-size: 1.8rem; font-weight: 700; }}
.stat .label {{ font-size: 0.8rem; color: var(--text-dim); text-transform: uppercase; }}
.dimension {{ background: var(--surface); border: 1px solid var(--border);
              border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; }}
.dimension h2 {{ font-size: 1.2rem; margin-bottom: 1rem; color: var(--accent); }}
.score-bar-container {{ background: var(--border); border-radius: 8px; height: 28px;
                        position: relative; margin-bottom: 1rem; overflow: hidden; }}
.score-bar {{ height: 100%; border-radius: 8px; transition: width 0.5s ease; }}
.score-label {{ position: absolute; right: 10px; top: 50%; transform: translateY(-50%);
                font-weight: 600; font-size: 0.85rem; }}
.summary {{ color: var(--text-dim); margin-bottom: 1rem; font-size: 0.95rem; }}
.finding {{ padding: 0.8rem 1rem; border-left: 3px solid var(--border);
            margin-bottom: 0.5rem; border-radius: 0 6px 6px 0; background: rgba(0,0,0,0.2); }}
.finding strong {{ display: block; margin-bottom: 0.3rem; }}
.finding p {{ font-size: 0.9rem; color: var(--text-dim); margin-top: 0.3rem; }}
.finding .rec {{ font-style: italic; color: var(--accent); opacity: 0.8; }}
.finding .location {{ font-size: 0.8rem; color: var(--text-dim); }}
.sev-critical {{ border-color: #ef4444; }}
.sev-error {{ border-color: #f97316; }}
.sev-warning {{ border-color: #eab308; }}
.sev-info {{ border-color: #38bdf8; }}
.sev-pass {{ border-color: #22c55e; }}
.badge {{ display: inline-block; padding: 0.1rem 0.5rem; border-radius: 4px;
          font-size: 0.7rem; font-weight: 700; margin-right: 0.5rem; }}
.sev-critical .badge {{ background: #ef4444; color: white; }}
.sev-error .badge {{ background: #f97316; color: white; }}
.sev-warning .badge {{ background: #eab308; color: #1e293b; }}
.sev-info .badge {{ background: #38bdf8; color: #1e293b; }}
.sev-pass .badge {{ background: #22c55e; color: #1e293b; }}
.no-findings {{ color: var(--text-dim); font-style: italic; }}
.req-table {{ width: 100%; border-collapse: collapse; font-size: 0.9rem; }}
.req-table th {{ text-align: left; padding: 0.7rem; border-bottom: 2px solid var(--border);
                 color: var(--text-dim); font-size: 0.8rem; text-transform: uppercase; }}
.req-table td {{ padding: 0.6rem 0.7rem; border-bottom: 1px solid var(--border); }}
.req-table .evidence {{ font-size: 0.8rem; color: var(--text-dim); max-width: 200px;
                        overflow: hidden; text-overflow: ellipsis; }}
.status-badge {{ display: inline-block; padding: 0.15rem 0.6rem; border-radius: 4px;
                 font-size: 0.75rem; font-weight: 600; color: white; }}
footer {{ text-align: center; padding: 2rem; color: var(--text-dim); font-size: 0.8rem; }}
</style>
</head>
<body>
<nav>
    <span class="brand">Project Validator</span>
    {nav_links}
</nav>
<main>
    <div class="hero">
        <div class="score-circle"><span class="value">{score:.0f}</span></div>
        <h1>{html.escape(report.project_name)}</h1>
        <p class="meta">{report.timestamp.strftime('%Y-%m-%d %H:%M')} &middot; {report.project_path}</p>
    </div>
    <div class="stats">
        <div class="stat"><div class="num" style="color:#22c55e">{report.pass_count}</div><div class="label">Passed</div></div>
        <div class="stat"><div class="num" style="color:#eab308">{report.warning_count}</div><div class="label">Warnings</div></div>
        <div class="stat"><div class="num" style="color:#f97316">{report.error_count}</div><div class="label">Errors</div></div>
        <div class="stat"><div class="num" style="color:#ef4444">{report.critical_count}</div><div class="label">Critical</div></div>
    </div>
    {dimensions_html}
    {req_section}
</main>
<footer>Generated by Project Validator v1.0 — Powered by Claude</footer>
</body>
</html>"""

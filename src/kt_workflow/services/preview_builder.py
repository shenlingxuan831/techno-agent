"""将汇编后的 Markdown + chart JSON 转为可浏览器打开的 HTML 预览（不做 PDF 渲染）。"""

from __future__ import annotations

import html
import json
import re
from typing import Any

_CHART_BLOCK_RE = re.compile(
    r"<!-- chart:(?P<id>[^ ]+) \((?P<ref>[^)]+)\) -->\s*```json\s*(?P<body>.*?)\s*```",
    re.DOTALL,
)

_CHART_SENTINEL_START = "<!--BP-CHART-START:{id}-->"
_CHART_SENTINEL_END = "<!--BP-CHART-END:{id}-->"

_EVIDENCE_RE = re.compile(r"【(事实|推断|待验证)(?:/[^】]+)?】")


def _esc(text: str) -> str:
    return html.escape(text or "", quote=False)


def _tag_evidence(text: str) -> str:
    def _sub(m: re.Match[str]) -> str:
        kind = m.group(1)
        css = {"事实": "fact", "推断": "infer", "待验证": "pending"}.get(kind, "pending")
        return f'<span class="evidence evidence-{css}">【{kind}】</span>'

    return _EVIDENCE_RE.sub(_sub, text)


def _render_table_html(columns: list[str], rows: list[list[str]], *, caption: str = "") -> str:
    head = "".join(f"<th>{_tag_evidence(_esc(str(c)))}</th>" for c in columns)
    body_rows = []
    for i, row in enumerate(rows):
        cells = row if isinstance(row, list) else [row]
        tds = "".join(f"<td>{_tag_evidence(_esc(str(c)))}</td>" for c in cells)
        zebra = " class='alt'" if i % 2 else ""
        body_rows.append(f"<tr{zebra}>{tds}</tr>")
    cap = f"<caption>{_esc(caption)}</caption>" if caption else ""
    return (
        f"<div class='table-wrap'><table class='bp-table'>{cap}"
        f"<thead><tr>{head}</tr></thead>"
        f"<tbody>{''.join(body_rows)}</tbody></table></div>"
    )


def _render_table_spec(spec: dict[str, Any]) -> str:
    return _render_table_html(
        list(spec.get("columns") or []),
        list(spec.get("rows") or []),
        caption=str(spec.get("caption") or ""),
    )


def _render_chart_block(chart: dict[str, Any], *, module_id: str = "", ref: str = "") -> str:
    ctype = str(chart.get("chart_type") or "unknown")
    title = _esc(str(chart.get("title") or "图表"))
    spec = chart.get("spec") or {}
    if not isinstance(spec, dict):
        spec = {"raw": spec}

    inner = ""
    if ctype == "table":
        inner = _render_table_spec(spec)
    elif ctype == "mermaid":
        source = str(spec.get("source") or "")
        inner = f"<div class='mermaid-wrap'><pre class='mermaid'>{_esc(source)}</pre></div>"
    elif ctype == "image_ref":
        uri = _esc(str(spec.get("storage_uri") or ""))
        alt = _esc(str(spec.get("alt") or title))
        inner = (
            f"<figure class='chart-figure'>"
            f"<img src='{uri}' alt='{alt}' loading='lazy'/>"
            f"<figcaption>{alt}</figcaption>"
            f"</figure>"
        )
    elif ctype == "placeholder":
        note = _esc(str(spec.get("note") or "图表占位，待组员实现"))
        suggested = _esc(str(spec.get("suggested_chart_type") or ""))
        status = _esc(str(spec.get("status") or "scaffold"))
        inner = (
            f"<div class='chart-placeholder'>"
            f"<p><strong>状态</strong>：{status}</p>"
            f"<p><strong>建议类型</strong>：{suggested or '—'}</p>"
            f"<p>{note}</p>"
            f"</div>"
        )
    else:
        inner = f"<pre class='chart-raw'>{_esc(json.dumps(chart, ensure_ascii=False, indent=2))}</pre>"

    meta = ""
    if module_id:
        meta = f"<p class='chart-meta'>{_esc(ref)} · <code>{_esc(module_id)}</code></p>"

    return (
        f"<section class='chart-block chart-{ctype}'>"
        f"<h4 class='chart-title'>{title} <span class='badge'>{ctype}</span></h4>"
        f"{meta}"
        f"{inner}"
        f"</section>"
    )


def _replace_chart_blocks(markdown: str) -> str:
    def _sub(match: re.Match[str]) -> str:
        mid = match.group("id")
        ref = match.group("ref")
        raw = match.group("body").strip()
        try:
            chart = json.loads(raw)
        except json.JSONDecodeError:
            chart = {"chart_type": "raw", "title": f"{ref}", "spec": {"json_error": True, "body": raw}}
        block = _render_chart_block(
            chart if isinstance(chart, dict) else {"spec": chart},
            module_id=mid,
            ref=ref,
        )
        start = _CHART_SENTINEL_START.format(id=mid)
        end = _CHART_SENTINEL_END.format(id=mid)
        wrapped = f"<div class='chart-anchor' id='chart-{_esc(mid)}'>{block}</div>"
        return f"{start}{wrapped}{end}"

    return _CHART_BLOCK_RE.sub(_sub, markdown)


def _inline_md(text: str) -> str:
    s = _esc(text)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", s)
    return _tag_evidence(s)


def _is_table_row(line: str) -> bool:
    s = line.strip()
    return s.startswith("|") and s.endswith("|") and s.count("|") >= 2


def _is_table_sep(line: str) -> bool:
    return bool(re.match(r"^\|[\s:|\-]+\|$", line.strip()))


def _parse_table_cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _render_md_table(lines: list[str]) -> str:
    if len(lines) < 2:
        return "\n".join(lines)
    columns = _parse_table_cells(lines[0])
    body_start = 2 if len(lines) > 1 and _is_table_sep(lines[1]) else 1
    rows = [_parse_table_cells(line) for line in lines[body_start:] if _is_table_row(line)]
    return _render_table_html(columns, rows)


def _simple_md_to_html(text: str) -> str:
    """轻量 Markdown → HTML（足够预览 BP 段落）。"""
    lines = text.splitlines()
    out: list[str] = []
    in_code = False
    code_buf: list[str] = []
    para_buf: list[str] = []
    list_buf: list[str] = []
    table_buf: list[str] = []
    list_ordered = False

    def flush_para() -> None:
        if not para_buf:
            return
        para = " ".join(s.strip() for s in para_buf if s.strip())
        if para:
            out.append(f"<p>{_inline_md(para)}</p>")
        para_buf.clear()

    def flush_list() -> None:
        if not list_buf:
            return
        tag = "ol" if list_ordered else "ul"
        items = "".join(f"<li>{_inline_md(item)}</li>" for item in list_buf)
        out.append(f"<{tag} class='bp-list'>{items}</{tag}>")
        list_buf.clear()

    def flush_table() -> None:
        if not table_buf:
            return
        out.append(_render_md_table(table_buf))
        table_buf.clear()

    for line in lines:
        if line.strip().startswith("```"):
            if in_code:
                out.append(f"<pre class='code-block'><code>{_esc(chr(10).join(code_buf))}</code></pre>")
                code_buf.clear()
                in_code = False
            else:
                flush_para()
                flush_list()
                flush_table()
                in_code = True
            continue
        if in_code:
            code_buf.append(line)
            continue

        stripped = line.strip()
        if _is_table_row(stripped):
            flush_para()
            flush_list()
            table_buf.append(stripped)
            continue

        flush_table()

        if not stripped:
            flush_para()
            flush_list()
            continue

        bullet = re.match(r"^[-*]\s+(.+)$", stripped)
        ordered = re.match(r"^\d+\.\s+(.+)$", stripped)
        if bullet:
            flush_para()
            if list_buf and list_ordered:
                flush_list()
            list_ordered = False
            list_buf.append(bullet.group(1).strip())
            continue
        if ordered:
            flush_para()
            if list_buf and not list_ordered:
                flush_list()
            list_ordered = True
            list_buf.append(ordered.group(1).strip())
            continue

        flush_list()
        if stripped.startswith("# "):
            flush_para()
            out.append(f"<h1 class='doc-title'>{_inline_md(stripped[2:].strip())}</h1>")
            continue
        if stripped.startswith("## "):
            flush_para()
            title = stripped[3:].strip()
            out.append(f"<h2 id='{_heading_id(title)}'>{_inline_md(title)}</h2>")
            continue
        if stripped.startswith("### "):
            flush_para()
            out.append(f"<h3>{_inline_md(stripped[4:].strip())}</h3>")
            continue
        if stripped.startswith("> "):
            flush_para()
            out.append(f"<blockquote>{_inline_md(stripped[2:].strip())}</blockquote>")
            continue
        if stripped == "---":
            flush_para()
            out.append("<hr class='section-divider'/>")
            continue
        para_buf.append(line)

    flush_para()
    flush_list()
    flush_table()
    return "\n".join(out)


def _split_chart_sentinels(text: str) -> list[tuple[str, str]]:
    """返回 [('md'|'html', content), ...] 交替片段。"""
    pattern = re.compile(
        r"<!--BP-CHART-START:(?P<id>[^>]+)-->(?P<body>.*?)<!--BP-CHART-END:\1-->",
        re.DOTALL,
    )
    parts: list[tuple[str, str]] = []
    cursor = 0
    for match in pattern.finditer(text):
        if match.start() > cursor:
            parts.append(("md", text[cursor:match.start()]))
        parts.append(("html", match.group("body")))
        cursor = match.end()
    if cursor < len(text):
        parts.append(("md", text[cursor:]))
    return parts


def _heading_id(title: str) -> str:
    slug = re.sub(r"[^\w\u4e00-\u9fff]+", "-", title.strip()).strip("-").lower()
    return slug or "section"


def _bp_styles() -> str:
    return """
    :root {
      --bg: #eef2f7;
      --card: #ffffff;
      --text: #1e293b;
      --muted: #64748b;
      --accent: #2563eb;
      --accent-soft: #eff6ff;
      --border: #e2e8f0;
      --placeholder: #fff8e1;
      --fact: #047857;
      --fact-bg: #ecfdf5;
      --infer: #b45309;
      --infer-bg: #fffbeb;
      --pending: #b91c1c;
      --pending-bg: #fef2f2;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.75;
      font-size: 15px;
    }
    header {
      background: linear-gradient(135deg, #1e3a5f 0%, #2563eb 60%, #3b82f6 100%);
      color: #fff;
      padding: 1.25rem 2rem;
      position: sticky;
      top: 0;
      z-index: 20;
      box-shadow: 0 2px 12px rgba(15,23,42,.15);
    }
    header h1 { margin: 0 0 0.25rem; font-size: 1.4rem; font-weight: 600; }
    header p { margin: 0; opacity: 0.9; font-size: 0.85rem; }
    main {
      max-width: 920px;
      margin: 1.5rem auto 2.5rem;
      padding: 0 1rem;
    }
    article {
      background: var(--card);
      border-radius: 12px;
      box-shadow: 0 1px 3px rgba(15,23,42,.06), 0 8px 24px rgba(15,23,42,.06);
      padding: 2rem 2.25rem;
      overflow: hidden;
    }
    article > * { max-width: 100%; }
    .doc-title {
      font-size: 1.55rem;
      border-bottom: 2px solid var(--accent);
      padding-bottom: 0.5rem;
      margin: 0 0 1.5rem;
    }
    h2 {
      font-size: 1.15rem;
      margin: 2rem 0 0.85rem;
      padding: 0.5rem 0 0.5rem 0.85rem;
      color: #0f172a;
      border-left: 4px solid var(--accent);
      background: linear-gradient(90deg, var(--accent-soft) 0%, transparent 70%);
      border-radius: 0 6px 6px 0;
    }
    article > h2:first-of-type { margin-top: 0.25rem; }
    h3 { font-size: 1.02rem; margin: 1.1rem 0 0.5rem; color: #334155; font-weight: 600; }
    p { margin: 0.55rem 0; text-align: justify; }
    .bp-list, ul, ol { margin: 0.45rem 0 0.75rem; padding-left: 1.4rem; }
    li { margin: 0.3rem 0; }
    blockquote {
      margin: 0.75rem 0;
      padding: 0.6rem 0.95rem;
      background: #f0f9ff;
      border-left: 3px solid #38bdf8;
      color: #0c4a6e;
      border-radius: 0 6px 6px 0;
      font-size: 0.95rem;
    }
    code {
      background: #f1f5f9;
      padding: 0.1em 0.35em;
      border-radius: 3px;
      font-size: 0.86em;
    }
    pre.code-block, pre.chart-raw {
      background: #0f172a;
      color: #e2e8f0;
      padding: 0.85rem 1rem;
      border-radius: 8px;
      overflow-x: auto;
      font-size: 0.82rem;
    }
    .evidence {
      display: inline-block;
      font-size: 0.76em;
      font-weight: 600;
      padding: 0.08em 0.42em;
      border-radius: 4px;
      margin-right: 0.2em;
      vertical-align: baseline;
      white-space: nowrap;
    }
    .evidence-fact { color: var(--fact); background: var(--fact-bg); }
    .evidence-infer { color: var(--infer); background: var(--infer-bg); }
    .evidence-pending { color: var(--pending); background: var(--pending-bg); }
    .table-wrap {
      overflow-x: auto;
      margin: 0.85rem 0 1rem;
      border: 1px solid var(--border);
      border-radius: 8px;
      background: #fff;
    }
    .bp-table, .chart-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.88rem;
      min-width: 420px;
    }
    .bp-table th, .bp-table td,
    .chart-table th, .chart-table td {
      border-bottom: 1px solid var(--border);
      padding: 0.55rem 0.75rem;
      text-align: left;
      vertical-align: middle;
    }
    .bp-table th, .chart-table th {
      background: #f1f5f9;
      color: #334155;
      font-weight: 600;
      white-space: nowrap;
      border-bottom: 2px solid #cbd5e1;
    }
    .bp-table tr:last-child td,
    .chart-table tr:last-child td { border-bottom: none; }
    .bp-table tr.alt td, .chart-table tr.alt td { background: #f8fafc; }
    .bp-table td:first-child, .chart-table td:first-child { font-weight: 500; color: #334155; }
    .chart-anchor {
      margin: 1rem 0 1.25rem;
      padding: 1rem 1.1rem;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      background: #f8fafc;
    }
    .chart-block { margin: 0; padding: 0; }
    .chart-title {
      margin: 0 0 0.65rem;
      font-size: 0.95rem;
      color: #475569;
      font-weight: 600;
    }
    .chart-meta {
      margin: 0 0 0.5rem;
      font-size: 0.72rem;
      color: var(--muted);
      opacity: 0.75;
    }
    .badge {
      display: inline-block;
      font-size: 0.65rem;
      background: #94a3b8;
      color: #fff;
      padding: 0.1rem 0.45rem;
      border-radius: 999px;
      vertical-align: middle;
      font-weight: 500;
      text-transform: lowercase;
    }
    .mermaid-wrap {
      margin: 0.5rem 0;
      padding: 0.75rem;
      background: #fafbfc;
      border: 1px solid var(--border);
      border-radius: 8px;
      overflow-x: auto;
    }
    pre.mermaid {
      margin: 0;
      background: transparent;
      border: none;
      padding: 0;
      color: inherit;
      font-size: 0.82rem;
    }
    .chart-placeholder {
      background: var(--placeholder);
      border: 1px solid #fcd34d;
      border-radius: 6px;
      padding: 0.75rem 1rem;
    }
    .chart-figure { margin: 0.5rem 0; text-align: center; }
    .chart-figure img {
      max-width: 100%;
      border-radius: 6px;
      border: 1px solid var(--border);
    }
    .section-divider {
      border: none;
      border-top: 1px dashed var(--border);
      margin: 1.5rem 0;
    }
    hr { border: none; border-top: 1px solid var(--border); margin: 1.25rem 0; }
    footer {
      text-align: center;
      color: var(--muted);
      font-size: 0.78rem;
      padding: 0.5rem 1rem 1.5rem;
    }
    @media print {
      header { position: static; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
      body { background: #fff; }
      article { box-shadow: none; padding: 0; }
      .chart-meta { display: none; }
      h2 { break-after: avoid; }
      .table-wrap, .mermaid-wrap { break-inside: avoid; }
    }
    """


def build_preview_html(
    *,
    document_title: str,
    markdown_body: str,
    run_id: str,
    project_name: str = "",
) -> str:
    """生成单文件 HTML，双击即可在浏览器预览组员产出。"""
    with_charts = _replace_chart_blocks(markdown_body)
    parts: list[str] = []
    for kind, chunk in _split_chart_sentinels(with_charts):
        if kind == "html":
            parts.append(chunk)
        else:
            parts.append(_simple_md_to_html(chunk))

    body_html = "\n".join(parts)
    subtitle = _esc(project_name or run_id)

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>{_esc(document_title)} — 预览</title>
  <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
  <style>{_bp_styles()}</style>
</head>
<body>
  <header>
    <h1>{_esc(document_title)}</h1>
    <p>BP 预览 · {subtitle}</p>
  </header>
  <main>
    <article>
{body_html}
    </article>
  </main>
  <footer>证据标签：【事实】 【推断】 【待验证】</footer>
  <script>
    if (window.mermaid) {{
      mermaid.initialize({{
        startOnLoad: true,
        theme: "neutral",
        securityLevel: "loose",
        flowchart: {{ htmlLabels: true, curve: "basis", padding: 12, nodeSpacing: 40 }}
      }});
    }}
  </script>
</body>
</html>
"""

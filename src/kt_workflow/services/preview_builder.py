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


def _esc(text: str) -> str:
    return html.escape(text or "", quote=False)


def _render_table_spec(spec: dict[str, Any]) -> str:
    columns = spec.get("columns") or []
    rows = spec.get("rows") or []
    head = "".join(f"<th>{_esc(str(c))}</th>" for c in columns)
    body_rows = []
    for row in rows:
        cells = row if isinstance(row, list) else [row]
        tds = "".join(f"<td>{_esc(str(c))}</td>" for c in cells)
        body_rows.append(f"<tr>{tds}</tr>")
    caption = spec.get("caption")
    cap = f"<caption>{_esc(str(caption))}</caption>" if caption else ""
    return f"<table class='chart-table'>{cap}<thead><tr>{head}</tr></thead><tbody>{''.join(body_rows)}</tbody></table>"


def _render_chart_block(chart: dict[str, Any]) -> str:
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
        inner = f"<pre class='mermaid'>{_esc(source)}</pre>"
    elif ctype == "image_ref":
        uri = _esc(str(spec.get("storage_uri") or ""))
        alt = _esc(str(spec.get("alt") or title))
        inner = f"<p class='chart-image-ref'><strong>图片引用</strong>：<code>{uri}</code></p><p class='muted'>{alt}</p>"
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

    return (
        f"<section class='chart-block chart-{ctype}'>"
        f"<h4 class='chart-title'>{title} <span class='badge'>{ctype}</span></h4>"
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
        block = _render_chart_block(chart if isinstance(chart, dict) else {"spec": chart})
        return (
            f"<div class='chart-anchor' id='chart-{_esc(mid)}'>"
            f"<p class='chart-label'>图表 · <code>{_esc(mid)}</code> · {_esc(ref)}</p>"
            f"{block}"
            f"</div>"
        )

    return _CHART_BLOCK_RE.sub(_sub, markdown)


def _simple_md_to_html(text: str) -> str:
    """轻量 Markdown → HTML（足够预览 BP 段落）。"""
    lines = text.splitlines()
    out: list[str] = []
    in_code = False
    code_buf: list[str] = []

    def flush_para(buf: list[str]) -> None:
        if not buf:
            return
        para = " ".join(s.strip() for s in buf if s.strip())
        if para:
            out.append(f"<p>{_inline_md(para)}</p>")
        buf.clear()

    para_buf: list[str] = []

    for line in lines:
        if line.strip().startswith("```"):
            if in_code:
                out.append(f"<pre><code>{_esc(chr(10).join(code_buf))}</code></pre>")
                code_buf.clear()
                in_code = False
            else:
                flush_para(para_buf)
                in_code = True
            continue
        if in_code:
            code_buf.append(line)
            continue

        stripped = line.strip()
        if not stripped:
            flush_para(para_buf)
            continue
        if stripped.startswith("# "):
            flush_para(para_buf)
            out.append(f"<h1>{_inline_md(stripped[2:].strip())}</h1>")
            continue
        if stripped.startswith("## "):
            flush_para(para_buf)
            out.append(f"<h2>{_inline_md(stripped[3:].strip())}</h2>")
            continue
        if stripped.startswith("### "):
            flush_para(para_buf)
            out.append(f"<h3>{_inline_md(stripped[4:].strip())}</h3>")
            continue
        if stripped.startswith("> "):
            flush_para(para_buf)
            out.append(f"<blockquote>{_inline_md(stripped[2:].strip())}</blockquote>")
            continue
        if stripped == "---":
            flush_para(para_buf)
            out.append("<hr/>")
            continue
        para_buf.append(line)

    flush_para(para_buf)
    return "\n".join(out)


def _inline_md(text: str) -> str:
    s = _esc(text)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", s)
    return s


def build_preview_html(
    *,
    document_title: str,
    markdown_body: str,
    run_id: str,
    project_name: str = "",
) -> str:
    """生成单文件 HTML，双击即可在浏览器预览组员产出。"""
    with_charts = _replace_chart_blocks(markdown_body)
    # 图表块已是 HTML；其余按段落切分后分别转 MD
    parts: list[str] = []
    cursor = 0
    for m in re.finditer(r"<div class='chart-anchor'", with_charts):
        start = m.start()
        if start > cursor:
            parts.append(_simple_md_to_html(with_charts[cursor:start]))
        # find closing </div> for chart-anchor — chart blocks are flat one div
        end = with_charts.find("</div>", start)
        if end == -1:
            parts.append(with_charts[start:])
            cursor = len(with_charts)
            break
        end += len("</div>")
        parts.append(with_charts[start:end])
        cursor = end
    if cursor < len(with_charts):
        parts.append(_simple_md_to_html(with_charts[cursor:]))

    body_html = "\n".join(parts)
    subtitle = _esc(project_name or run_id)

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>{_esc(document_title)} — 预览</title>
  <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
  <style>
    :root {{
      --bg: #f6f7fb;
      --card: #ffffff;
      --text: #1a1a2e;
      --muted: #5c6370;
      --accent: #2563eb;
      --border: #e5e7eb;
      --placeholder: #fff8e1;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.65;
    }}
    header {{
      background: linear-gradient(135deg, #1e3a5f, #2563eb);
      color: #fff;
      padding: 1.25rem 2rem;
    }}
    header h1 {{ margin: 0 0 0.25rem; font-size: 1.35rem; }}
    header p {{ margin: 0; opacity: 0.9; font-size: 0.9rem; }}
    main {{
      max-width: 920px;
      margin: 1.5rem auto 3rem;
      padding: 0 1rem;
    }}
    article {{
      background: var(--card);
      border-radius: 12px;
      box-shadow: 0 2px 12px rgba(0,0,0,.06);
      padding: 2rem 2.25rem;
    }}
    h1 {{ font-size: 1.6rem; border-bottom: 2px solid var(--accent); padding-bottom: 0.35rem; }}
    h2 {{ font-size: 1.25rem; margin-top: 1.75rem; color: #0f172a; border-left: 4px solid var(--accent); padding-left: 0.6rem; }}
    h3 {{ font-size: 1.05rem; margin-top: 1.25rem; }}
    blockquote {{
      margin: 0.75rem 0;
      padding: 0.5rem 1rem;
      background: #f0f9ff;
      border-left: 4px solid #38bdf8;
      color: #0c4a6e;
    }}
    code {{
      background: #f1f5f9;
      padding: 0.1em 0.35em;
      border-radius: 4px;
      font-size: 0.88em;
    }}
    pre {{
      background: #0f172a;
      color: #e2e8f0;
      padding: 1rem;
      border-radius: 8px;
      overflow-x: auto;
      font-size: 0.85rem;
    }}
    .chart-anchor {{
      margin: 1.25rem 0;
      padding: 1rem;
      border: 1px dashed var(--border);
      border-radius: 8px;
      background: #fafafa;
    }}
    .chart-label {{ margin: 0 0 0.5rem; font-size: 0.85rem; color: var(--muted); }}
    .chart-title {{ margin: 0 0 0.75rem; font-size: 1rem; }}
    .badge {{
      display: inline-block;
      font-size: 0.7rem;
      background: var(--accent);
      color: #fff;
      padding: 0.1rem 0.45rem;
      border-radius: 4px;
      vertical-align: middle;
    }}
    .chart-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.9rem;
    }}
    .chart-table th, .chart-table td {{
      border: 1px solid var(--border);
      padding: 0.45rem 0.6rem;
      text-align: left;
    }}
    .chart-table th {{ background: #eff6ff; }}
    .chart-placeholder {{
      background: var(--placeholder);
      border: 1px solid #fcd34d;
      border-radius: 6px;
      padding: 0.75rem 1rem;
    }}
    .muted {{ color: var(--muted); font-size: 0.9rem; }}
    hr {{ border: none; border-top: 1px solid var(--border); margin: 1.5rem 0; }}
    footer {{
      text-align: center;
      color: var(--muted);
      font-size: 0.8rem;
      padding: 1rem;
    }}
  </style>
</head>
<body>
  <header>
    <h1>{_esc(document_title)}</h1>
    <p>预览模式 · run_id={_esc(run_id)} · {subtitle}</p>
  </header>
  <main>
    <article>
{body_html}
    </article>
  </main>
  <footer>kt_workflow HTML 预览（非 PDF）· 图表占位会以黄色框显示</footer>
  <script>
    if (window.mermaid) {{
      mermaid.initialize({{ startOnLoad: true, theme: "neutral" }});
    }}
  </script>
</body>
</html>
"""

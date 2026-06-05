"""Export docs/*.md to docs_txt/*.html for browser viewing and Word copy-paste."""

from __future__ import annotations

import re
from pathlib import Path

import markdown
from bs4 import BeautifulSoup, NavigableString
from markdown.extensions.tables import TableExtension

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "docs"
DST_DIR = ROOT / "docs_txt"

# Inline styles tuned for Microsoft Word paste (CF_HTML / MSO)
WORD_TABLE = (
    "border-collapse:collapse;mso-table-layout-alt:fixed;"
    "mso-yfti-tbllook:1184;mso-padding-alt:0cm 5.4pt 0cm 5.4pt;"
    "width:100%;border:none;mso-border-alt:solid windowtext .5pt;"
)
WORD_TH = (
    "border:solid windowtext 1.0pt;mso-border-alt:solid windowtext 1.0pt;"
    "padding:4.0pt 6.0pt;background:#F2F2F2;mso-shading:windowtext;"
    "mso-pattern:gray-10 auto;font-weight:bold;vertical-align:top;"
)
WORD_TD = (
    "border:solid windowtext 1.0pt;mso-border-alt:solid windowtext 1.0pt;"
    "padding:4.0pt 6.0pt;vertical-align:top;"
)
BODY_STYLE = (
    'font-family:"Microsoft YaHei","PingFang SC",SimSun,Arial,sans-serif;'
    "font-size:11.0pt;line-height:1.35;color:#000000;"
)
HEADING_STYLES = {
    "h1": (
        "font-size:22.0pt;font-weight:bold;"
        "margin-top:8.0pt;margin-bottom:4.0pt;margin-left:0;margin-right:0;"
        "border-bottom:1.5pt solid #333;padding-bottom:2pt;"
    ),
    "h2": (
        "font-size:16.0pt;font-weight:bold;"
        "margin-top:6.0pt;margin-bottom:3.0pt;margin-left:0;margin-right:0;"
        "border-bottom:0.75pt solid #999;padding-bottom:2pt;"
    ),
    "h3": (
        "font-size:13.0pt;font-weight:bold;"
        "margin-top:4.0pt;margin-bottom:2.0pt;margin-left:0;margin-right:0;"
    ),
    "h4": (
        "font-size:11.5pt;font-weight:bold;"
        "margin-top:3.0pt;margin-bottom:2.0pt;margin-left:0;margin-right:0;"
    ),
}
P_STYLE = "margin-top:2.0pt;margin-bottom:2.0pt;line-height:1.35;"
LI_STYLE = "margin-top:0;margin-bottom:0;line-height:1.35;"
OL_STYLE = "margin-top:1.0pt;margin-bottom:3.0pt;padding-left:22pt;line-height:1.35;"
UL_STYLE = "margin-top:1.0pt;margin-bottom:3.0pt;padding-left:22pt;line-height:1.35;"
BLOCKQUOTE_STYLE = (
    "margin-top:4.0pt;margin-bottom:4.0pt;padding:4pt 10pt;"
    "border-left:3pt solid #0066CC;background:#F7F9FC;"
    "mso-border-left-alt:solid #0066CC 3.0pt;"
)
PRE_STYLE = (
    "font-family:Consolas,'Courier New',monospace;font-size:9.5pt;"
    "background:#F6F8FA;border:0.75pt solid #CCCCCC;padding:6pt;"
    "white-space:pre-wrap;word-wrap:break-word;line-height:1.35;"
    "margin-top:3.0pt;margin-bottom:3.0pt;"
)
CODE_STYLE = (
    "font-family:Consolas,'Courier New',monospace;font-size:10.0pt;"
    "background:#F4F4F4;padding:0 3pt;"
)
HR_STYLE = (
    "border:none;border-top:0.75pt solid #CCCCCC;"
    "margin-top:5.0pt;margin-bottom:5.0pt;height:0;line-height:0;"
)
TABLE_STYLE_EXTRA = "margin-top:3.0pt;margin-bottom:3.0pt;"

COPY_BUTTON_JS = """
function copyDocForWord() {
  var src = document.getElementById('doc-content');
  if (!src) { alert('未找到正文区域'); return; }
  var wrapper = '<html xmlns:o="urn:schemas-microsoft-com:office:office" '
    + 'xmlns:w="urn:schemas-microsoft-com:office:word">'
    + '<head><meta charset="UTF-8"></head>'
    + '<body style="' + src.getAttribute('data-body-style') + '">'
    + src.innerHTML + '</body></html>';
  var plain = src.innerText || src.textContent;
  if (navigator.clipboard && window.ClipboardItem) {
    var item = new ClipboardItem({
      'text/html': new Blob([wrapper], { type: 'text/html' }),
      'text/plain': new Blob([plain], { type: 'text/plain' })
    });
    navigator.clipboard.write([item]).then(function () {
      showCopyOk();
    }).catch(function () { fallbackCopy(wrapper, plain); });
  } else {
    fallbackCopy(wrapper, plain);
  }
}
function fallbackCopy(html, plain) {
  var ta = document.createElement('textarea');
  ta.value = plain;
  ta.style.position = 'fixed';
  ta.style.left = '-9999px';
  document.body.appendChild(ta);
  ta.select();
  try { document.execCommand('copy'); showCopyOk(); }
  catch (e) { alert('复制失败，请手动拖选正文后 Ctrl+C'); }
  document.body.removeChild(ta);
}
function showCopyOk() {
  var btn = document.getElementById('copy-word-btn');
  if (!btn) return;
  var old = btn.textContent;
  btn.textContent = '已复制，请到 Word 中 Ctrl+V';
  btn.style.background = '#2e7d32';
  setTimeout(function () {
    btn.textContent = old;
    btn.style.background = '#0066cc';
  }, 2500);
}
"""

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN" xmlns:o="urn:schemas-microsoft-com:office:office"
      xmlns:w="urn:schemas-microsoft-com:office:word">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="ProgId" content="Word.Document">
<meta name="Generator" content="Microsoft Word">
<title>{title}</title>
<!--[if gte mso 9]><xml>
<w:WordDocument><w:View>Print</w:View><w:Zoom>100</w:Zoom></w:WordDocument>
</xml><![endif]-->
<style>
  body {{
    font-family: "Microsoft YaHei", "PingFang SC", SimSun, Arial, sans-serif;
    font-size: 11pt;
    line-height: 1.5;
    color: #000;
    max-width: 920px;
    margin: 0 auto;
    padding: 24px 32px 48px;
    background: #fff;
  }}
  .toolbar {{
    background: #f0f4f8;
    border: 1px solid #c5d3e0;
    padding: 12px 16px;
    margin-bottom: 20px;
    font-size: 10.5pt;
  }}
  .toolbar button {{
    background: #0066cc;
    color: #fff;
    border: none;
    padding: 8px 18px;
    font-size: 11pt;
    cursor: pointer;
    border-radius: 4px;
    margin-right: 12px;
  }}
  .toolbar button:hover {{ background: #0052a3; }}
  .toolbar .hint {{ color: #555; }}
  .nav {{ margin-bottom: 16px; font-size: 10pt; }}
  .nav a {{ color: #0066cc; }}
</style>
<script>{copy_js}</script>
</head>
<body>
<div class="toolbar">
  <button type="button" id="copy-word-btn" onclick="copyDocForWord()">复制正文到 Word</button>
  <span class="hint">推荐：点按钮复制 → 打开 Word → Ctrl+V（保留源格式）。比 Ctrl+A 粘贴更稳。</span>
</div>
{nav}
<div id="doc-content" data-body-style="{body_style}">
{body}
</div>
{extra}
</body>
</html>
"""

INDEX_EXTRA = """
<div class="toolbar" style="margin-top:24px;">
  <span class="hint"><strong>发给组员：</strong>打包整个 docs_txt 文件夹；双击 index.html 打开。
  仓库：<a href="https://github.com/shenlingxuan831/techno-agent.git">techno-agent</a>，分支 feature-Xiao。</span>
</div>
"""


def prepare_markdown(text: str) -> str:
    text = re.sub(
        r"\[REPOSITORY_LAYOUT\.md\]\(\.\./REPOSITORY_LAYOUT\.md\)",
        "REPOSITORY_LAYOUT.md（见仓库根目录，未收录在本文件夹）",
        text,
    )
    text = text.replace("docs/", "")
    for md in sorted(SRC_DIR.glob("*.md")):
        if md.name == "README.md":
            continue
        text = text.replace(f"{md.stem}.md", f"{md.stem}.html")
    return text


def md_to_html(md_text: str) -> str:
    return markdown.markdown(
        md_text,
        extensions=[
            TableExtension(),
            "fenced_code",
            "sane_lists",
        ],
        output_format="html5",
    )


def _set_style(tag, style: str) -> None:
    existing = tag.get("style", "")
    tag["style"] = f"{existing};{style}" if existing else style


def _is_hr_div(tag) -> bool:
    return tag.name == "div" and "border-top:0.75pt solid #CCCCCC" in tag.get("style", "")


def _replace_margin_top(tag, value: str) -> None:
    style = tag.get("style", "")
    if "margin-top:" in style:
        style = re.sub(r"margin-top:[^;]+;", f"margin-top:{value};", style)
    else:
        style = f"margin-top:{value};{style}"
    tag["style"] = style


def _replace_margin_bottom(tag, value: str) -> None:
    style = tag.get("style", "")
    if "margin-bottom:" in style:
        style = re.sub(r"margin-bottom:[^;]+;", f"margin-bottom:{value};", style)
    else:
        style = f"{style};margin-bottom:{value};"
    tag["style"] = style


def _compact_vertical_rhythm(soup: BeautifulSoup) -> None:
    """Tighten gaps between headings, lists, and horizontal rules."""
    for el in soup.find_all(["h1", "h2", "h3", "h4", "ol", "ul", "p", "table"]):
        prev = el.find_previous_sibling()
        if prev is None:
            continue
        if _is_hr_div(prev) and el.name in HEADING_STYLES:
            _replace_margin_top(el, "3.0pt")
        elif prev.name in HEADING_STYLES and el.name in ("ol", "ul", "p"):
            _replace_margin_top(el, "0")
            _replace_margin_bottom(prev, "1.0pt")
        elif prev.name in ("ol", "ul") and el.name in HEADING_STYLES:
            _replace_margin_top(el, "3.0pt")
        elif _is_hr_div(prev):
            _replace_margin_top(el, "3.0pt")


def wordify_html(html: str) -> str:
    """Add Word-friendly inline styles; flatten table wrappers; fix empty cells."""
    soup = BeautifulSoup(html, "html.parser")

    for table in soup.find_all("table"):
        table["border"] = "1"
        table["cellspacing"] = "0"
        table["cellpadding"] = "0"
        _set_style(table, WORD_TABLE)
        _set_style(table, TABLE_STYLE_EXTRA)
        for wrapper in table.find_all(["thead", "tbody", "tfoot"]):
            wrapper.unwrap()
        for th in table.find_all("th"):
            _set_style(th, WORD_TH)
        for td in table.find_all("td"):
            _set_style(td, WORD_TD)
            if not td.get_text(strip=True) and not td.find(["img", "br", "ul", "ol", "table"]):
                td.clear()
                td.append(NavigableString("\u00a0"))

    for tag_name, style in HEADING_STYLES.items():
        for el in soup.find_all(tag_name):
            _set_style(el, style)

    for p in soup.find_all("p"):
        _set_style(p, P_STYLE)

    for li in soup.find_all("li"):
        _set_style(li, LI_STYLE)

    for ol in soup.find_all("ol"):
        _set_style(ol, OL_STYLE)

    for ul in soup.find_all("ul"):
        _set_style(ul, UL_STYLE)

    for bq in soup.find_all("blockquote"):
        bq.name = "div"
        bq["class"] = "blockquote"
        _set_style(bq, BLOCKQUOTE_STYLE)

    for pre in soup.find_all("pre"):
        _set_style(pre, PRE_STYLE)
        for code in pre.find_all("code"):
            code.attrs.pop("style", None)

    for code in soup.find_all("code"):
        if code.parent and code.parent.name == "pre":
            continue
        _set_style(code, CODE_STYLE)

    for hr in soup.find_all("hr"):
        hr.name = "div"
        hr.clear()
        _set_style(hr, HR_STYLE)

    for strong in soup.find_all("strong"):
        _set_style(strong, "font-weight:bold;")

    _compact_vertical_rhythm(soup)

    return str(soup)


def page_title(stem: str, md_text: str) -> str:
    if stem == "index":
        return "文档索引 — 科技成果转化智能体"
    first_line = md_text.strip().splitlines()[0] if md_text.strip() else stem
    if first_line.startswith("#"):
        return first_line.lstrip("# ").strip()
    return stem


def write_page(
    out_path: Path,
    title: str,
    body_html: str,
    *,
    is_index: bool = False,
) -> None:
    extra = INDEX_EXTRA if is_index else ""
    nav = "" if is_index else '<div class="nav"><a href="index.html">← 返回文档索引</a></div>\n'
    html = HTML_TEMPLATE.format(
        title=title,
        body=body_html,
        nav=nav,
        extra=extra,
        copy_js=COPY_BUTTON_JS,
        body_style=BODY_STYLE.replace('"', "&quot;"),
    )
    out_path.write_text(html, encoding="utf-8")


def main() -> None:
    DST_DIR.mkdir(exist_ok=True)
    for old_txt in DST_DIR.glob("*.txt"):
        old_txt.unlink()

    for md in sorted(SRC_DIR.glob("*.md")):
        raw = md.read_text(encoding="utf-8")
        prepared = prepare_markdown(raw)
        body = wordify_html(md_to_html(prepared))
        if md.name == "README.md":
            out_name = "index.html"
            is_index = True
        else:
            out_name = f"{md.stem}.html"
            is_index = False
        title = page_title("index" if is_index else md.stem, raw)
        write_page(DST_DIR / out_name, title, body, is_index=is_index)
        print(f"  {md.name} -> {out_name}")

    print(f"Done: {len(list(DST_DIR.glob('*.html')))} HTML files in docs_txt/")


if __name__ == "__main__":
    main()

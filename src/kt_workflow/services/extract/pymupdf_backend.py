"""Layer 1 兜底 — PyMuPDF 抽文本 + 嵌图导出。"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from kt_workflow.services.extract.types import FigureRecord


def parse_pdf_with_pymupdf(
    pdf_path: Path,
    figures_dir: Path,
) -> tuple[str, str, list[FigureRecord], dict[str, Any]]:
    """返回 (plain_text, markdown, figures, meta)。"""
    import fitz

    figures_dir.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(str(pdf_path))
    text_parts: list[str] = []
    md_parts: list[str] = [f"# {pdf_path.stem}\n"]
    figures: list[FigureRecord] = []
    fig_idx = 0

    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        page_text = (page.get_text() or "").strip()
        text_parts.append(page_text)
        md_parts.append(f"\n## 第 {page_num + 1} 页\n\n{page_text}\n")

        for img_info in page.get_images(full=True):
            xref = img_info[0]
            try:
                base = doc.extract_image(xref)
            except Exception:
                continue
            if not base or not base.get("image"):
                continue
            ext = base.get("ext", "png")
            w, h = base.get("width"), base.get("height")
            if (w or 0) < 80 or (h or 0) < 80:
                continue
            fig_idx += 1
            fig_id = f"fig_p{page_num + 1:02d}_{fig_idx:02d}"
            fname = f"{fig_id}.{ext}"
            out_path = figures_dir / fname
            out_path.write_bytes(base["image"])
            rel_uri = str(out_path.as_posix())
            figures.append(
                FigureRecord(
                    fig_id=fig_id,
                    page=page_num + 1,
                    storage_uri=rel_uri,
                    width=w,
                    height=h,
                    priority_score=float(w or 0) * float(h or 0) / 1_000_000,
                )
            )
            md_parts.append(f"\n![{fig_id}]({fname})\n")

    doc.close()
    plain = "\n\n".join(text_parts).strip()
    markdown = "\n".join(md_parts).strip()
    meta = {
        "backend": "pymupdf",
        "page_count": len(text_parts),
        "figure_count": len(figures),
    }
    return plain, markdown, figures, meta

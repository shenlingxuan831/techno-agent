"""PDF 类型粗判：数字文本层 vs 扫描/图片型。"""

from __future__ import annotations

from io import BytesIO
from typing import Any


def classify_pdf(data: bytes) -> dict[str, Any]:
    """返回 {pdf_kind, chars_per_page, page_count, has_images}。"""
    try:
        import fitz
    except ImportError:
        import pypdf

        reader = pypdf.PdfReader(BytesIO(data))
        pages = reader.pages
        texts = [(p.extract_text() or "") for p in pages]
        page_count = len(texts)
        char_total = sum(len(t.strip()) for t in texts)
        cpp = char_total / max(page_count, 1)
        kind = "digital_text" if cpp >= 120 else "scan_or_image"
        return {
            "pdf_kind": kind,
            "chars_per_page": round(cpp, 1),
            "page_count": page_count,
            "has_images": None,
            "classifier": "pypdf",
        }

    doc = fitz.open(stream=data, filetype="pdf")
    page_count = doc.page_count
    char_total = 0
    image_count = 0
    for i in range(page_count):
        page = doc.load_page(i)
        char_total += len((page.get_text() or "").strip())
        image_count += len(page.get_images(full=True))
    doc.close()

    cpp = char_total / max(page_count, 1)
    if cpp >= 120:
        kind = "digital_text"
    elif cpp >= 30:
        kind = "mixed"
    else:
        kind = "scan_or_image"

    return {
        "pdf_kind": kind,
        "chars_per_page": round(cpp, 1),
        "page_count": page_count,
        "has_images": image_count > 0,
        "image_count": image_count,
        "classifier": "pymupdf",
    }

"""Layer 2 — 从 MinerU/PyMuPDF 产物建立图目录与图注对齐。"""

from __future__ import annotations

import re
import shutil
from pathlib import Path
from typing import Any

from kt_workflow.services.extract.types import FigureRecord

_CAPTION_RE = re.compile(
    r"(?:Figure|Fig\.?|图\s*\d+)[^\n]{0,200}",
    re.IGNORECASE,
)
_IMG_MD_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
_FIGURE_TYPE_HINTS = {
    "chart": ("curve", "plot", "graph", "performance", "曲线", "性能", "对比"),
    "diagram": ("architecture", "framework", "flow", "schematic", "架构", "流程", "示意"),
    "photo": ("photo", "microscopy", "sem", "tem", "电镜", "照片"),
    "table_image": ("table", "表格"),
    "formula": ("equation", "公式"),
}


def _guess_figure_type(caption: str, alt: str) -> str:
    blob = f"{caption} {alt}".lower()
    for ftype, hints in _FIGURE_TYPE_HINTS.items():
        if any(h in blob for h in hints):
            return ftype
    return "unknown"


def _score_figure(rec: FigureRecord) -> float:
    score = rec.priority_score
    cap = (rec.caption or "").strip()
    if cap:
        score += 5.0
    if _CAPTION_RE.search(cap):
        score += 3.0
    if rec.figure_type in ("chart", "diagram"):
        score += 2.0
    if rec.width and rec.height:
        area = rec.width * rec.height
        if area > 400_000:
            score += 2.0
        elif area < 40_000:
            score -= 2.0
    return score


def _copy_image(src: Path, dest_dir: Path, fig_id: str) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    ext = src.suffix.lower() or ".png"
    dest = dest_dir / f"{fig_id}{ext}"
    if src.resolve() != dest.resolve():
        shutil.copy2(src, dest)
    return dest


def build_catalog_from_mineru(
    markdown: str,
    md_path: Path,
    source_dir: Path,
) -> list[FigureRecord]:
    """解析 MinerU Markdown 中的图片引用，复制到 source/figures/。"""
    figures_dir = source_dir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)
    md_dir = md_path.parent
    records: list[FigureRecord] = []
    seen: set[str] = set()

    for idx, match in enumerate(_IMG_MD_RE.finditer(markdown)):
        alt = match.group(1).strip()
        rel = match.group(2).strip()
        if rel in seen:
            continue
        seen.add(rel)

        img_path = (md_dir / rel).resolve()
        if not img_path.is_file():
            candidate = md_dir / "images" / Path(rel).name
            if candidate.is_file():
                img_path = candidate.resolve()
            else:
                continue

        fig_id = f"fig_{idx + 1:03d}"
        dest = _copy_image(img_path, figures_dir, fig_id)
        caption = alt
        # 在图片附近找 Figure/图 注
        pos = match.start()
        window = markdown[max(0, pos - 400) : min(len(markdown), pos + 400)]
        cap_m = _CAPTION_RE.search(window)
        if cap_m:
            caption = cap_m.group(0).strip()

        ftype = _guess_figure_type(caption, alt)
        try:
            from PIL import Image

            with Image.open(dest) as im:
                w, h = im.size
        except Exception:
            w, h = None, None

        rec = FigureRecord(
            fig_id=fig_id,
            page=None,
            storage_uri=str(dest.as_posix()),
            caption=caption,
            figure_type=ftype,
            width=w,
            height=h,
        )
        rec.priority_score = _score_figure(rec)
        records.append(rec)

    records.sort(key=lambda r: r.priority_score, reverse=True)
    return records


def finalize_figure_records(records: list[FigureRecord]) -> list[FigureRecord]:
    for rec in records:
        rec.priority_score = _score_figure(rec)
    records.sort(key=lambda r: r.priority_score, reverse=True)
    return records


def figures_to_json(records: list[FigureRecord]) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "figure_count": len(records),
        "figures": [r.to_dict() for r in records],
    }

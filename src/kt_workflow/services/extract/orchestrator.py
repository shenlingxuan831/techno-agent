"""三层 PDF 提取编排：MinerU → 图目录 → 视觉分析。"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

from kt_workflow.paths import kt_run_source_dir
from kt_workflow.services.extract.cache_env import apply_extract_cache_env
from kt_workflow.services.document_parser import extract_text_from_path
from kt_workflow.services.extract.figure_catalog import (
    build_catalog_from_mineru,
    figures_to_json,
    finalize_figure_records,
)
from kt_workflow.services.extract.figure_vision import analyze_figures_with_vision
from kt_workflow.services.extract.mineru_backend import mineru_available, parse_pdf_with_mineru
from kt_workflow.services.extract.pdf_classifier import classify_pdf
from kt_workflow.services.extract.pymupdf_backend import parse_pdf_with_pymupdf
from kt_workflow.services.extract.types import ExtractResult, FigureRecord
from kt_workflow.text_io import workspace_root


def _env_truthy(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in ("1", "true", "yes")


def _extract_backend() -> str:
    return os.getenv("KT_EXTRACT_BACKEND", "auto").strip().lower() or "auto"


def _max_chars() -> int:
    try:
        return int(os.getenv("KT_EXTRACT_MAX_CHARS", "120000"))
    except ValueError:
        return 120_000


def _truncate(text: str, limit: int) -> tuple[str, bool]:
    if len(text) <= limit:
        return text, False
    return text[:limit] + "\n\n…（已截断）", True


def _markdown_to_plain(md: str) -> str:
    text = md
    text = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _resolve_path(source_uri: str) -> Path:
    p = Path(source_uri.strip())
    if not p.is_absolute():
        p = workspace_root() / p
    return p.resolve()


def _save_markdown(source_dir: Path, markdown: str, stem: str) -> Path:
    md_path = source_dir / f"{stem}.md"
    md_path.write_text(markdown, encoding="utf-8")
    return md_path


def extract_pdf_layers(
    pdf_path: Path,
    *,
    run_id: str,
    project_name: str = "",
) -> ExtractResult:
    """PDF 三层提取主入口。"""
    apply_extract_cache_env()
    source_dir = kt_run_source_dir(run_id)
    data = pdf_path.read_bytes()
    classification = classify_pdf(data)
    meta: dict[str, Any] = {
        "source_path": str(pdf_path),
        "file_format": "pdf",
        "extractor": "extract_pdf_layers_v1",
        "byte_size": len(data),
        **classification,
    }

    backend_pref = _extract_backend()
    use_mineru = backend_pref in ("mineru", "auto") and mineru_available()
    if backend_pref == "mineru" and not mineru_available():
        meta["mineru_unavailable"] = True
        use_mineru = False

    markdown = ""
    plain = ""
    figures: list[FigureRecord] = []
    md_saved: Path | None = None

    if use_mineru and not _env_truthy("KT_EXTRACT_MOCK"):
        try:
            markdown, md_path, mineru_meta = parse_pdf_with_mineru(pdf_path, source_dir)
            meta.update(mineru_meta)
            if markdown.strip():
                md_saved = _save_markdown(source_dir, markdown, pdf_path.stem)
                figures = build_catalog_from_mineru(markdown, md_path or md_saved, source_dir)
                plain = _markdown_to_plain(markdown)
                meta["layer1"] = "mineru"
        except Exception as exc:
            meta["mineru_error"] = str(exc)
            use_mineru = False

    if not markdown.strip():
        figures_dir = source_dir / "figures"
        plain, markdown, figures, pymupdf_meta = parse_pdf_with_pymupdf(pdf_path, figures_dir)
        meta.update(pymupdf_meta)
        meta["layer1"] = "pymupdf_fallback"
        md_saved = _save_markdown(source_dir, markdown, pdf_path.stem)

    figures = finalize_figure_records(figures)
    meta["figure_count"] = len(figures)

    figure_analysis, vision_meta = analyze_figures_with_vision(
        figures,
        project_name=project_name,
    )
    meta["vision"] = vision_meta
    meta["layer2"] = "figure_catalog"
    meta["layer3"] = "figure_vision"

    limit = _max_chars()
    markdown, md_trunc = _truncate(markdown, limit)
    plain, plain_trunc = _truncate(plain or _markdown_to_plain(markdown), limit)
    meta["truncated"] = md_trunc or plain_trunc
    meta["max_chars"] = limit
    meta["char_count"] = len(plain)
    meta["markdown_char_count"] = len(markdown)

    if md_saved and markdown:
        md_saved.write_text(markdown, encoding="utf-8")
        meta["extracted_markdown_path"] = str(md_saved)

    return ExtractResult(
        plain_text=plain,
        markdown=markdown,
        figures=figures,
        figure_analysis=figure_analysis,
        meta=meta,
    )


def extract_document(
    source_uri: str,
    *,
    run_id: str | None = None,
    project_name: str = "",
    max_chars: int | None = None,
) -> ExtractResult:
    """统一入口：PDF 走三层；其他格式走 legacy parser。"""
    if not source_uri.strip():
        return ExtractResult(
            plain_text="[extract] 未提供 source_uri。",
            markdown="",
            meta={"error": "missing_source_uri", "extractor": "extract_document_v1"},
        )

    path = _resolve_path(source_uri)
    if not path.is_file():
        msg = f"[extract] 路径不存在或非文件: {path}"
        return ExtractResult(
            plain_text=msg,
            markdown="",
            meta={"error": "not_found", "resolved_path": str(path)},
        )

    if path.suffix.lower() == ".pdf" and run_id:
        result = extract_pdf_layers(path, run_id=run_id, project_name=project_name)
        if max_chars is not None:
            plain, t1 = _truncate(result.plain_text, max_chars)
            md, t2 = _truncate(result.markdown, max_chars)
            result.plain_text = plain
            result.markdown = md
            result.meta["truncated"] = result.meta.get("truncated") or t1 or t2
        return result

    limit = max_chars or _max_chars()
    text, parse_meta = extract_text_from_path(path, max_chars=limit)
    return ExtractResult(
        plain_text=text,
        markdown=text,
        meta={
            "source_uri": source_uri,
            "resolved_path": str(path),
            "extractor": "document_parser_legacy",
            **parse_meta,
        },
    )

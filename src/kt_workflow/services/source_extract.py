"""从 source_uri 读取正文，供 extract 节点调用（支持 PDF/Word/PPT/Excel 等）。"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from kt_workflow.services.document_parser import extract_text_from_path
from kt_workflow.text_io import workspace_root


def _resolve_source_path(source_uri: str) -> Path:
    p = Path(source_uri.strip())
    if not p.is_absolute():
        p = workspace_root() / p
    return p.resolve()


def extract_from_source_uri(source_uri: str, max_chars: int = 50_000) -> tuple[str, dict[str, Any]]:
    """返回 (正文, 写入 kt_artifacts meta_json 的字段)。"""
    if not source_uri.strip():
        return "[extract] 未提供 source_uri。", {
            "source_uri": source_uri,
            "char_count": 0,
            "error": "missing_source_uri",
            "extractor": "source_extract_v2",
        }

    path = _resolve_source_path(source_uri)
    text, parse_meta = extract_text_from_path(path, max_chars=max_chars)
    meta: dict[str, Any] = {
        "source_uri": source_uri,
        "resolved_path": str(path),
        "char_count": parse_meta.get("char_count", len(text)),
        "max_chars": max_chars,
        "truncated": parse_meta.get("truncated", False),
        "file_format": parse_meta.get("file_format"),
        "extractor": "source_extract_v2",
    }
    meta.update({k: v for k, v in parse_meta.items() if k not in meta})
    return text, meta

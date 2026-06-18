"""从 source_uri 读取正文，供 extract 节点调用（PDF 三层 + 其他格式 legacy）。"""

from __future__ import annotations

from typing import Any

from kt_workflow.services.extract import ExtractResult, extract_document


def extract_from_source_uri(
    source_uri: str,
    *,
    run_id: str | None = None,
    project_name: str = "",
    max_chars: int | None = None,
) -> ExtractResult:
    """返回 ExtractResult（plain_text、markdown、figures、figure_analysis、meta）。"""
    return extract_document(
        source_uri,
        run_id=run_id,
        project_name=project_name,
        max_chars=max_chars,
    )


def extract_meta_for_artifact(result: ExtractResult, source_uri: str) -> dict[str, Any]:
    meta: dict[str, Any] = {
        "source_uri": source_uri,
        "char_count": len(result.plain_text),
        "markdown_char_count": len(result.markdown),
        "figure_count": len(result.figures),
        "extractor": result.meta.get("extractor", "extract_document_v1"),
    }
    meta.update(result.meta)
    return meta

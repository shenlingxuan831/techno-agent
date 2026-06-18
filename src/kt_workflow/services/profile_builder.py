"""由 extracted_text + LLM 分析 + 入参状态构造 structured_profile。"""

from __future__ import annotations

import json
import re
from collections import Counter
from typing import Any

from sqlalchemy.orm import Session

from kt_workflow import constants as C
from kt_workflow.repositories import artifacts as art_repo
from kt_workflow.state import KTWorkflowState


_SCHEMA_VERSION = 4
_EXCERPT_LIMIT = 8_000

_STOP_CN = {
    "我们", "可以", "一个", "进行", "通过", "以及", "及其", "用于", "基于", "该", "一种", "没有", "已经",
    "本文", "本项", "涉及", "主要", "包括", "采用", "实现", "相关", "例如", "其中",
}


def _top_keywords(text: str, n: int = 12) -> list[str]:
    if not text.strip():
        return []
    chunks = re.findall(r"[\u4e00-\u9fff]{2,}", text)
    chunks += re.findall(r"[A-Za-z][A-Za-z0-9_.-]{1,}", text)
    filtered = [c for c in chunks if c not in _STOP_CN]
    return [w for w, _ in Counter(filtered).most_common(n)]


def _trl_hint(text: str) -> str | None:
    m = re.search(r"TRL\s*[：:\s]*(\d+(?:\s*[-~～–]\s*\d+)?)", text, re.IGNORECASE)
    if m:
        return f"TRL {m.group(1).strip()}"
    m = re.search(r"(?:约|大约)?\s*(\d+)\s*[-~～]?\s*(\d+)?\s*级", text)
    if m:
        if m.group(2):
            return f"约 {m.group(1)}-{m.group(2)} 级（原文表述）"
        return f"约 {m.group(1)} 级（原文表述）"
    return None


def _load_figure_analysis(session: Session, run_id: str) -> dict[str, Any] | None:
    raw = art_repo.get_latest_text(session, run_id, C.FIGURE_ANALYSIS, "default")
    if not raw or not raw.strip():
        return None
    try:
        parsed = json.loads(raw)
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        return None


def _load_llm_analysis(session: Session, run_id: str) -> dict[str, Any] | None:
    raw = art_repo.get_latest_text(session, run_id, C.LLM_SOURCE_ANALYSIS, "default")
    if not raw or not raw.strip():
        return None
    try:
        parsed = json.loads(raw)
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        return None


def _slim_figures_block(figure_analysis: dict[str, Any] | None) -> dict[str, Any]:
    if not figure_analysis:
        return {"count": 0, "aggregate_summary": "", "items": []}
    items = []
    for fig in figure_analysis.get("figures") or []:
        if not isinstance(fig, dict) or fig.get("error"):
            continue
        items.append(
            {
                "fig_id": fig.get("fig_id"),
                "caption": fig.get("caption", ""),
                "figure_type": fig.get("figure_type", "unknown"),
                "summary": fig.get("summary", ""),
            }
        )
    return {
        "count": len(items),
        "aggregate_summary": figure_analysis.get("aggregate_summary") or "",
        "items": items[:12],
    }


def build_structured_profile(
    extracted_text: str | None,
    state: KTWorkflowState,
    *,
    llm_analysis: dict[str, Any] | None = None,
    extracted_markdown: str | None = None,
    figure_analysis: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """纯函数：不访问数据库。"""
    md = (extracted_markdown or "").strip()
    text = md or (extracted_text or "").strip()
    excerpt = text[:_EXCERPT_LIMIT] if text else ""
    llm_keywords = []
    if llm_analysis and isinstance(llm_analysis.get("keywords"), list):
        llm_keywords = [str(k) for k in llm_analysis["keywords"] if str(k).strip()]

    rule_keywords = _top_keywords(text)
    merged_keywords = list(dict.fromkeys(llm_keywords + rule_keywords))[:20]

    trl_hint = _trl_hint(text)
    if llm_analysis and llm_analysis.get("trl_level"):
        trl_hint = str(llm_analysis["trl_level"])

    profile: dict[str, Any] = {
        "schema_version": _SCHEMA_VERSION,
        "source": {
            "source_uri": state.source_uri or "",
            "excerpt_char_length": len(text),
            "extractor_profile": "profile_builder_v4_llm" if llm_analysis else "profile_builder_v4_rules_only",
            "has_markdown": bool(md),
        },
        "submission": {
            "project_name": state.project_name or "",
            "user_type": state.user_type or "",
            "contact_info": state.contact_info or "",
            "specific_requirements": state.specific_requirements or "",
        },
        "content": {
            "excerpt": excerpt,
            "keywords_top": merged_keywords,
            "trl_hint": trl_hint,
        },
        "analysis": llm_analysis or {},
        "figures": _slim_figures_block(figure_analysis),
        "downstream": {
            "note": "各章生成服务可读 analysis、figures 与 content；v4 起含插图视觉摘要。",
        },
    }
    return profile


def materialize_profile_for_run(session: Session, state: KTWorkflowState) -> tuple[dict[str, Any], dict[str, Any]]:
    """读库中 extract/analyze 产物，生成 profile v4。"""
    raw = art_repo.get_latest_text(session, state.run_id, C.EXTRACTED_TEXT, "default")
    markdown = art_repo.get_latest_text(session, state.run_id, C.EXTRACTED_MARKDOWN, "default")
    llm_analysis = _load_llm_analysis(session, state.run_id)
    figure_analysis = _load_figure_analysis(session, state.run_id)
    profile = build_structured_profile(
        raw,
        state,
        llm_analysis=llm_analysis,
        extracted_markdown=markdown,
        figure_analysis=figure_analysis,
    )
    has_extract = bool((raw or markdown or "").strip())
    meta = {
        "schema_version": profile["schema_version"],
        "builder": "profile_builder_v4",
        "missing_extract": not has_extract,
        "has_llm_analysis": bool(llm_analysis),
        "has_figure_analysis": bool(figure_analysis),
        "has_markdown": bool(markdown and markdown.strip()),
    }
    if llm_analysis is None:
        meta["llm_analysis_missing"] = True
    return profile, meta

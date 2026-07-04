"""Analyze 阶段商业化字段二次补强（综述/论文 → 可转化场景）。"""

from __future__ import annotations

import json
import re
from typing import Any

from jinja2 import Template
from langchain_core.messages import HumanMessage, SystemMessage

from kt_workflow.services.llm_client import kt_llm_client, kt_llm_model
from kt_workflow.services.source_analyzer import _build_figure_context, _extract_json_object
from kt_workflow.state import KTWorkflowState
from kt_workflow.text_io import workspace_root

_CFG_REL = "config/kt_source_commercial_llm_cfg.json"
_EXCERPT_LIMIT = 12_000

_LIST_KEYS = (
    "application_scenarios",
    "commercialization_barriers",
    "data_gaps",
    "commercialization_opportunities",
)
_STR_KEYS = (
    "target_market",
    "competitive_landscape",
    "policy_fit_hint",
    "document_type",
)


def _load_cfg() -> dict[str, Any]:
    path = workspace_root() / _CFG_REL
    if not path.is_file():
        raise FileNotFoundError(f"缺少商业化补强配置: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _is_sparse_commercial(analysis: dict[str, Any]) -> bool:
    tm = str(analysis.get("target_market") or "").strip()
    if not tm or tm in ("待验证", "【待验证】"):
        return True
    scenarios = analysis.get("application_scenarios") or []
    if not isinstance(scenarios, list) or len(scenarios) < 2:
        return True
    return False


def _looks_like_review(source_text: str, analysis: dict[str, Any]) -> bool:
    doc_type = str(analysis.get("document_type") or "").lower()
    if doc_type == "review":
        return True
    head = source_text[:4000].lower()
    if "review" in head or "综述" in source_text[:4000]:
        return True
    if re.search(r"\ba\s+review\b", head):
        return True
    return False


def should_enrich_commercial(source_text: str, analysis: dict[str, Any]) -> bool:
    return _looks_like_review(source_text, analysis) or _is_sparse_commercial(analysis)


def _merge_list_field(base: list[Any], patch: list[Any], limit: int = 8) -> list[str]:
    items: list[str] = []
    seen: set[str] = set()
    for raw in list(base) + list(patch):
        text = str(raw).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        items.append(text)
        if len(items) >= limit:
            break
    return items


def merge_commercial_patch(analysis: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    merged = dict(analysis)
    for key in _LIST_KEYS:
        if key not in patch:
            continue
        patch_val = patch.get(key)
        if not isinstance(patch_val, list):
            continue
        base_val = merged.get(key) or []
        if not isinstance(base_val, list):
            base_val = [base_val] if base_val else []
        merged[key] = _merge_list_field(base_val, patch_val)
    for key in _STR_KEYS:
        if key not in patch:
            continue
        val = patch.get(key)
        if val is None:
            continue
        text = str(val).strip()
        if not text or text in ("待验证", "【待验证】"):
            continue
        existing = str(merged.get(key) or "").strip()
        if not existing or existing in ("待验证", "【待验证】"):
            merged[key] = text
    return merged


def enrich_commercial_fields(
    source_text: str,
    state: KTWorkflowState,
    analysis: dict[str, Any],
    *,
    figure_analysis: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    meta: dict[str, Any] = {"cfg_path": _CFG_REL, "skipped": False}
    if not should_enrich_commercial(source_text, analysis):
        meta["skipped"] = True
        meta["reason"] = "commercial_fields_sufficient"
        return analysis, meta

    excerpt = source_text[:_EXCERPT_LIMIT]
    meta["source_excerpt_chars"] = len(excerpt)
    meta["trigger"] = "review" if _looks_like_review(source_text, analysis) else "sparse_fields"

    cfg = _load_cfg()
    llm_cfg = cfg.get("config", {})
    model = kt_llm_model(str(llm_cfg.get("model", "deepseek-chat")))
    figure_context = _build_figure_context(figure_analysis)

    sp = Template(cfg.get("sp", "")).render()
    up = Template(cfg.get("up", "")).render(
        project_name=state.project_name or "未命名",
        user_type=state.user_type or "高校",
        primary_analysis_json=json.dumps(analysis, ensure_ascii=False, indent=2),
        figure_context=figure_context,
        excerpt_chars=len(excerpt),
        source_excerpt=excerpt,
    )

    client = kt_llm_client()
    response = client.invoke(
        messages=[SystemMessage(content=sp), HumanMessage(content=up)],
        model=model,
        temperature=float(llm_cfg.get("temperature", 0.35)),
        top_p=float(llm_cfg.get("top_p", 0.95)),
        max_completion_tokens=int(llm_cfg.get("max_completion_tokens", 4096)),
    )
    content = response.content
    raw = content.strip() if isinstance(content, str) else str(content)
    patch = _extract_json_object(raw)
    meta["model"] = model
    meta["patch_keys"] = list(patch.keys())
    return merge_commercial_patch(analysis, patch), meta

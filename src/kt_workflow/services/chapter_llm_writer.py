"""叙述型 BP 小节 LLM 生成（执行摘要、背景、结论等）。"""

from __future__ import annotations

import json
import os
import re
from collections.abc import Callable
from typing import Any

from jinja2 import Template
from langchain_core.messages import HumanMessage, SystemMessage

from kt_workflow.services.chapter_writer_contract import ChapterWriterContext
from kt_workflow.services.llm_client import analysis_mock_enabled, kt_llm_client, kt_llm_model
from kt_workflow.text_io import workspace_root

_CFG_REL = "config/kt_chapter_narrative_llm_cfg.json"
_ANALYSIS_KEYS = (
    "summary",
    "tech_name",
    "trl_level",
    "trl_rationale",
    "tech_innovation",
    "innovation_detail",
    "advantages",
    "disadvantages",
    "application_scenarios",
    "target_market",
    "competitive_landscape",
    "ip_status",
    "team_and_resources",
    "commercialization_barriers",
    "policy_fit_hint",
    "keywords",
    "data_gaps",
    "document_type",
    "commercialization_opportunities",
    "figure_evidence_summary",
    "experimental_evidence_from_figures",
)


def _env_truthy(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in ("1", "true", "yes")


def chapter_llm_mock_enabled() -> bool:
    if _env_truthy("KT_CHAPTER_LLM_MOCK"):
        return True
    return analysis_mock_enabled()


def chapter_llm_enabled() -> bool:
    if os.getenv("KT_CHAPTER_LLM", "").strip().lower() in ("0", "false", "no"):
        return False
    return not chapter_llm_mock_enabled()


def _load_cfg() -> dict[str, Any]:
    path = workspace_root() / _CFG_REL
    if not path.is_file():
        raise FileNotFoundError(f"缺少章节 LLM 配置: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _trim_analysis(analysis: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key in _ANALYSIS_KEYS:
        if key not in analysis:
            continue
        val = analysis[key]
        if val in (None, "", [], {}):
            continue
        if isinstance(val, str) and len(val) > 480:
            out[key] = val[:477] + "…"
        elif isinstance(val, list):
            out[key] = [str(x)[:200] for x in val[:8]]
        else:
            out[key] = val
    return out


def _strip_heading(text: str) -> str:
    lines = text.splitlines()
    while lines and lines[0].strip().startswith("#"):
        lines.pop(0)
    while lines and not lines[0].strip():
        lines.pop(0)
    return "\n".join(lines).strip()


def _sanitize_body(text: str) -> str:
    body = _strip_heading(text.strip())
    body = re.sub(r"```[\s\S]*?```", "", body).strip()
    # 叙述型小节禁止 Markdown 表格
    if re.search(r"^\|.*\|$", body, re.MULTILINE):
        body = re.sub(r"^\|.*\|$", "", body, flags=re.MULTILINE).strip()
    return body


def generate_narrative_module_text(
    ctx: ChapterWriterContext,
    *,
    section_brief: str,
    word_limit: int = 300,
) -> str | None:
    """调用 LLM 生成小节正文（不含 ## 标题）。失败返回 None。"""
    if not chapter_llm_enabled():
        return None

    profile = ctx.get("profile") or {}
    analysis = profile.get("analysis") if isinstance(profile, dict) else {}
    if not isinstance(analysis, dict) or not analysis:
        return None

    mod = ctx.get("module") or {}
    cfg = _load_cfg()
    llm_cfg = cfg.get("config", {})
    model = kt_llm_model(str(llm_cfg.get("model", "deepseek-chat")))

    sp = Template(cfg.get("sp", "")).render()
    up = Template(cfg.get("up", "")).render(
        chapter_ref=str(mod.get("ref", "")),
        section_title=str(mod.get("title", "")),
        section_brief=section_brief,
        word_limit=word_limit,
        project_name=str(profile.get("submission", {}).get("project_name") or ctx.get("document_title") or "未命名"),
        user_type=str(profile.get("submission", {}).get("user_type") or "高校"),
        analysis_json=json.dumps(_trim_analysis(analysis), ensure_ascii=False, indent=2),
    )

    try:
        client = kt_llm_client()
        response = client.invoke(
            messages=[SystemMessage(content=sp), HumanMessage(content=up)],
            model=model,
            temperature=float(llm_cfg.get("temperature", 0.35)),
            top_p=float(llm_cfg.get("top_p", 0.95)),
            max_completion_tokens=int(llm_cfg.get("max_completion_tokens", 2048)),
        )
        content = response.content
        raw = content.strip() if isinstance(content, str) else str(content)
        body = _sanitize_body(raw)
        return body or None
    except Exception:
        return None


def write_narrative_with_fallback(
    ctx: ChapterWriterContext,
    heading: str,
    *,
    section_brief: str,
    word_limit: int,
    fallback: Callable[[], str],
) -> str:
    """LLM 优先；失败则走模板 fallback（fallback 应返回含 heading 的完整 Markdown）。"""
    body = generate_narrative_module_text(
        ctx, section_brief=section_brief, word_limit=word_limit
    )
    if body:
        return f"{heading}\n\n{body}\n"
    return fallback()

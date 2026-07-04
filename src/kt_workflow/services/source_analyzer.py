"""调用大模型分析 extracted_text，输出结构化 JSON（DeepSeek 等 OpenAI 兼容网关）。"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from jinja2 import Template
from langchain_core.messages import HumanMessage, SystemMessage

from kt_workflow.services.llm_client import analysis_mock_enabled, kt_llm_client, kt_llm_model
from kt_workflow.state import KTWorkflowState
from kt_workflow.text_io import workspace_root

_LLM_INPUT_LIMIT = 48_000
_CFG_REL = "config/kt_source_analysis_llm_cfg.json"


def _load_cfg(cfg_rel: str = _CFG_REL) -> dict[str, Any]:
    path = workspace_root() / cfg_rel
    if not path.is_file():
        raise FileNotFoundError(f"缺少 LLM 配置: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _extract_json_object(text: str) -> dict[str, Any]:
    raw = text.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw, re.IGNORECASE)
    if fence:
        raw = fence.group(1).strip()
    start = raw.find("{")
    end = raw.rfind("}")
    if start >= 0 and end > start:
        raw = raw[start : end + 1]
    parsed = json.loads(raw)
    if not isinstance(parsed, dict):
        raise ValueError("LLM 输出不是 JSON 对象")
    return parsed


def _mock_analysis(state: KTWorkflowState, source_text: str) -> dict[str, Any]:
    excerpt = source_text[:400]
    return {
        "summary": f"（MOCK）基于材料前 {len(excerpt)} 字的占位分析。",
        "tech_name": state.project_name or "待验证",
        "trl_level": "待验证",
        "trl_rationale": "KT_ANALYSIS_MOCK_LLM=1，未调用真实大模型",
        "tech_innovation": "中",
        "innovation_detail": "占位",
        "advantages": ["占位优势"],
        "disadvantages": ["占位风险"],
        "application_scenarios": ["占位场景"],
        "target_market": "待验证",
        "competitive_landscape": "待验证",
        "ip_status": "待验证",
        "team_and_resources": "待验证",
        "commercialization_barriers": ["待验证"],
        "policy_fit_hint": "待验证",
        "keywords": ["mock"],
        "data_gaps": ["关闭 MOCK 后重新运行以获取真实分析"],
    }


def _build_figure_context(figure_analysis: dict[str, Any] | None) -> str:
    if not figure_analysis:
        return "（无插图视觉分析）"
    lines: list[str] = []
    agg = (figure_analysis.get("aggregate_summary") or "").strip()
    if agg:
        lines.append(f"综合摘要：{agg}")
    for fig in figure_analysis.get("figures") or []:
        if not isinstance(fig, dict):
            continue
        if fig.get("error"):
            continue
        fid = fig.get("fig_id", "")
        summary = fig.get("summary", "")
        metrics = fig.get("metrics") or fig.get("experimental_findings") or []
        cap = fig.get("caption", "")
        block = f"- [{fid}] {cap}\n  摘要：{summary}"
        if metrics:
            block += "\n  要点：" + "；".join(str(m) for m in metrics[:5])
        trl = fig.get("trl_evidence")
        if trl:
            block += f"\n  成熟度线索：{trl}"
        lines.append(block)
    return "\n".join(lines) if lines else "（插图分析为空）"


def analyze_source_material(
    source_text: str,
    state: KTWorkflowState,
    *,
    figure_analysis: dict[str, Any] | None = None,
    cfg_rel: str = _CFG_REL,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    返回 (analysis_json, meta_for_artifact)。
    不访问数据库。
    """
    text = (source_text or "").strip()
    meta: dict[str, Any] = {
        "provider": "deepseek",
        "cfg_path": cfg_rel,
        "input_char_count": len(text),
        "has_figure_analysis": bool(figure_analysis),
        "mock": False,
    }

    if not text or text.startswith("[extract]") or text.startswith("[stub]"):
        empty = {
            "summary": "无有效正文，跳过大模型分析",
            "tech_name": state.project_name or "",
            "trl_level": "待验证",
            "trl_rationale": "",
            "tech_innovation": "待验证",
            "innovation_detail": "",
            "advantages": [],
            "disadvantages": [],
            "application_scenarios": [],
            "target_market": "待验证",
            "competitive_landscape": "待验证",
            "ip_status": "待验证",
            "team_and_resources": "待验证",
            "commercialization_barriers": [],
            "policy_fit_hint": "待验证",
            "keywords": [],
            "data_gaps": ["缺少可分析的 extracted_text"],
        }
        meta["skipped"] = True
        meta["reason"] = "empty_or_error_extract"
        return empty, meta

    llm_input = text
    if len(llm_input) > _LLM_INPUT_LIMIT:
        llm_input = llm_input[:_LLM_INPUT_LIMIT] + "\n\n…（送入模型的正文已截断）"
        meta["llm_input_truncated"] = True
    meta["llm_input_char_count"] = len(llm_input)

    if analysis_mock_enabled():
        meta["mock"] = True
        return _mock_analysis(state, text), meta

    figure_context = _build_figure_context(figure_analysis)
    meta["figure_context_chars"] = len(figure_context)

    cfg = _load_cfg(cfg_rel)
    llm_config = cfg.get("config", {})
    model = kt_llm_model(str(llm_config.get("model", "deepseek-chat")))

    sp_tpl = Template(cfg.get("sp", ""))
    up_tpl = Template(cfg.get("up", ""))
    system_prompt = sp_tpl.render()
    user_prompt = up_tpl.render(
        project_name=state.project_name or "未命名",
        user_type=state.user_type or "高校",
        specific_requirements=state.specific_requirements or "无",
        source_text=llm_input,
        figure_context=figure_context,
    )

    client = kt_llm_client()
    response = client.invoke(
        messages=[
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ],
        model=model,
        temperature=float(llm_config.get("temperature", 0.3)),
        top_p=float(llm_config.get("top_p", 0.95)),
        max_completion_tokens=int(llm_config.get("max_completion_tokens", 8192)),
    )
    content = response.content
    raw_out = content.strip() if isinstance(content, str) else str(content)
    meta["model"] = model
    meta["raw_response_chars"] = len(raw_out)

    analysis = _extract_json_object(raw_out)
    if figure_analysis:
        analysis["figure_evidence_summary"] = figure_analysis.get("aggregate_summary") or ""
        exp: list[str] = []
        for fig in figure_analysis.get("figures") or []:
            if isinstance(fig, dict):
                exp.extend(fig.get("experimental_findings") or [])
                exp.extend(fig.get("metrics") or [])
        if exp:
            analysis["experimental_evidence_from_figures"] = list(dict.fromkeys(str(x) for x in exp))[:12]

    try:
        from kt_workflow.services.commercial_enrichment import enrich_commercial_fields

        analysis, enrich_meta = enrich_commercial_fields(
            text,
            state,
            analysis,
            figure_analysis=figure_analysis,
        )
        meta["commercial_enrichment"] = enrich_meta
    except Exception as exc:
        meta["commercial_enrichment"] = {"skipped": True, "error": str(exc)}

    return analysis, meta

"""Layer 3a — 视觉大模型分析论文插图（OpenAI 兼容多模态 API）。"""

from __future__ import annotations

import base64
import json
import os
import re
from pathlib import Path
from typing import Any

from jinja2 import Template
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from kt_workflow.services.extract.types import FigureRecord
from kt_workflow.text_io import workspace_root

_CFG_REL = "config/kt_figure_vision_llm_cfg.json"
_MIME = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".gif": "image/gif",
}


def _env_truthy(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in ("1", "true", "yes")


def vision_mock_enabled() -> bool:
    if _env_truthy("KT_VISION_MOCK"):
        return True
    if _env_truthy("KT_VISION_FORCE"):
        return False
    key = (
        (os.getenv("KT_VISION_API_KEY") or "").strip()
        or (os.getenv("DASHSCOPE_API_KEY") or "").strip()
        or (os.getenv("OPENAI_API_KEY") or "").strip()
    )
    return not key


def _max_figures() -> int:
    try:
        return max(1, int(os.getenv("KT_MAX_FIGURES_FOR_VL", "8")))
    except ValueError:
        return 8


def _load_cfg() -> dict[str, Any]:
    path = workspace_root() / _CFG_REL
    if not path.is_file():
        raise FileNotFoundError(f"缺少视觉模型配置: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _vision_client(cfg: dict[str, Any]) -> ChatOpenAI:
    llm_cfg = cfg.get("config", {})
    api_key = (
        (os.getenv("KT_VISION_API_KEY") or "").strip()
        or (os.getenv("DASHSCOPE_API_KEY") or "").strip()
        or (os.getenv("DEEPSEEK_API_KEY") or "").strip()
        or (os.getenv("OPENAI_API_KEY") or "").strip()
        or (os.getenv("ARK_API_KEY") or "").strip()
    )
    base_url = (
        (os.getenv("KT_VISION_BASE_URL") or "").strip()
        or (os.getenv("OPENAI_BASE_URL") or "").strip()
        or (os.getenv("COZE_INTEGRATION_BASE_URL") or "").strip()
        or "https://dashscope.aliyuncs.com/compatible-mode/v1"
    )
    model = (
        (os.getenv("KT_VISION_MODEL") or "").strip()
        or str(llm_cfg.get("model", "qwen-vl-plus"))
    )
    return ChatOpenAI(
        model=model,
        api_key=api_key or None,
        base_url=base_url,
        temperature=float(llm_cfg.get("temperature", 0.2)),
        max_tokens=int(llm_cfg.get("max_completion_tokens", 2048)),
    )


def _image_to_data_url(path: Path) -> str:
    ext = path.suffix.lower()
    mime = _MIME.get(ext, "image/png")
    b64 = base64.standard_b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{b64}"


def _extract_json(text: str) -> dict[str, Any]:
    raw = text.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw, re.IGNORECASE)
    if fence:
        raw = fence.group(1).strip()
    start, end = raw.find("{"), raw.rfind("}")
    if start >= 0 and end > start:
        raw = raw[start : end + 1]
    parsed = json.loads(raw)
    if not isinstance(parsed, dict):
        raise ValueError("vision output not object")
    return parsed


def _mock_figure_analysis(records: list[FigureRecord]) -> dict[str, Any]:
    items = []
    for rec in records[: _max_figures()]:
        items.append(
            {
                "fig_id": rec.fig_id,
                "caption": rec.caption,
                "figure_type": rec.figure_type,
                "summary": f"（MOCK）占位图分析：{rec.fig_id}",
                "metrics": [],
                "experimental_findings": [],
                "commercial_relevance": "待验证",
                "trl_evidence": "待验证",
                "data_gaps": ["KT_VISION_MOCK=1"],
            }
        )
    return {
        "schema_version": 1,
        "model": "mock",
        "figures_analyzed": len(items),
        "figures": items,
        "aggregate_summary": "（MOCK）未调用视觉模型",
    }


def analyze_figures_with_vision(
    records: list[FigureRecord],
    *,
    project_name: str = "",
) -> tuple[dict[str, Any], dict[str, Any]]:
    """对 priority 最高的若干图调用 VL，返回 (figure_analysis_json, meta)。"""
    meta: dict[str, Any] = {
        "provider": "vision_openai_compatible",
        "cfg_path": _CFG_REL,
        "input_figure_count": len(records),
        "mock": False,
    }
    selected = records[: _max_figures()]
    meta["figures_selected"] = len(selected)

    if not selected:
        empty = {
            "schema_version": 1,
            "figures_analyzed": 0,
            "figures": [],
            "aggregate_summary": "无可用插图",
        }
        meta["skipped"] = True
        return empty, meta

    if vision_mock_enabled():
        meta["mock"] = True
        return _mock_figure_analysis(selected), meta

    cfg = _load_cfg()
    client = _vision_client(cfg)
    meta["model"] = client.model_name

    sp = Template(cfg.get("sp", "")).render()
    up_tpl = Template(cfg.get("up", ""))
    analyzed: list[dict[str, Any]] = []

    for rec in selected:
        img_path = Path(rec.storage_uri)
        if not img_path.is_file():
            analyzed.append(
                {
                    "fig_id": rec.fig_id,
                    "error": "image_not_found",
                    "storage_uri": rec.storage_uri,
                }
            )
            continue
        user_text = up_tpl.render(
            project_name=project_name or "未命名",
            fig_id=rec.fig_id,
            caption=rec.caption or "（无图注）",
            figure_type=rec.figure_type,
        )
        msg = HumanMessage(
            content=[
                {"type": "text", "text": user_text},
                {"type": "image_url", "image_url": {"url": _image_to_data_url(img_path)}},
            ]
        )
        try:
            resp = client.invoke([SystemMessage(content=sp), msg])
            content = resp.content if isinstance(resp.content, str) else str(resp.content)
            parsed = _extract_json(content)
            parsed.setdefault("fig_id", rec.fig_id)
            parsed.setdefault("caption", rec.caption)
            parsed.setdefault("storage_uri", rec.storage_uri)
            analyzed.append(parsed)
        except Exception as exc:
            analyzed.append(
                {
                    "fig_id": rec.fig_id,
                    "caption": rec.caption,
                    "error": str(exc),
                }
            )

    summaries = [a.get("summary", "") for a in analyzed if a.get("summary")]
    result = {
        "schema_version": 1,
        "model": meta.get("model"),
        "figures_analyzed": len(analyzed),
        "figures": analyzed,
        "aggregate_summary": "；".join(summaries[:5]) if summaries else "",
    }
    meta["figures_analyzed"] = len(analyzed)
    return result, meta

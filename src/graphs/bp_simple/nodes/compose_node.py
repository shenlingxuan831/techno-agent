"""简版 BP：按固定目录调用大模型生成 Markdown 并落盘。"""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

from jinja2 import Template
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_dev_sdk import LLMClient
from coze_coding_dev_sdk.core.config import Config
from coze_coding_utils.runtime_ctx.context import Context

from graphs.bp_simple.state import BPWorkflowState


def _env_truthy(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in ("1", "true", "yes")


def _llm_client_for_model() -> LLMClient:
    """模型网关 Bearer：方舟/OpenAI 兼容密钥与 Coze sk- 不同，优先使用专用环境变量。"""
    key = (
        (os.getenv("ARK_API_KEY") or "").strip()
        or (os.getenv("OPENAI_API_KEY") or "").strip()
        or (os.getenv("COZE_WORKLOAD_IDENTITY_API_KEY") or "").strip()
    )
    openai_base = (os.getenv("OPENAI_BASE_URL") or "").strip()
    if key and openai_base:
        return LLMClient(
            config=Config(api_key=key, base_url=openai_base, base_model_url=openai_base)
        )
    if key:
        return LLMClient(config=Config(api_key=key))
    return LLMClient()


def _load_outline() -> str:
    p = Path(__file__).resolve().parent.parent / "bp_outline.md"
    return p.read_text(encoding="utf-8")


def bp_simple_compose_node(
    state: BPWorkflowState,
    config: RunnableConfig,
    runtime: Runtime[Context],
) -> dict:
    workspace = os.getenv("COZE_WORKSPACE_PATH", os.getcwd())
    meta = config.get("metadata") or {}
    if isinstance(meta, dict):
        cfg_rel = meta.get("llm_cfg", "config/bp_simple_llm_cfg.json")
    else:
        cfg_rel = "config/bp_simple_llm_cfg.json"
    cfg_file = os.path.join(workspace, cfg_rel)

    import json

    with open(cfg_file, "r", encoding="utf-8") as fd:
        _cfg = json.load(fd)

    llm_config = _cfg.get("config", {})
    sp_tpl = Template(_cfg.get("sp", ""))
    up_tpl = Template(_cfg.get("up", ""))

    ark_model = (os.getenv("ARK_MODEL") or os.getenv("ARK_ENDPOINT_ID") or "").strip()
    model_id = ark_model or llm_config.get("model", "doubao-seed-2-0-pro-260215")

    outline = _load_outline()
    system_prompt = sp_tpl.render(outline=outline)

    tech_excerpt = (state.tech_text or "").strip()
    if len(tech_excerpt) > 12000:
        tech_excerpt = tech_excerpt[:12000] + "\n\n…（正文已截断，略）"

    user_prompt = up_tpl.render(
        tech_excerpt=tech_excerpt,
        user_type=state.user_type,
        contact_info=state.contact_info or "未提供",
        specific_requirements=state.specific_requirements or "无",
    )

    if _env_truthy("BP_SIMPLE_MOCK_LLM"):
        bp_markdown = (
            "# 商业计划书（MOCK）\n\n"
            "当前为 **BP_SIMPLE_MOCK_LLM** 占位输出，未请求大模型。\n\n"
            "## 摘要\n"
            f"- 技术摘录长度: {len(tech_excerpt)} 字符\n"
            "- 真实调用：在 `.env` 配置 `ARK_API_KEY`（或 `OPENAI_API_KEY` + "
            "`OPENAI_BASE_URL`）后，将 `BP_SIMPLE_MOCK_LLM` 删除或设为 `0`。\n"
        )
    else:
        client = _llm_client_for_model()
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]

        response = client.invoke(
            messages=messages,
            model=model_id,
            temperature=float(llm_config.get("temperature", 0.6)),
            max_completion_tokens=int(llm_config.get("max_completion_tokens", 8192)),
        )

        content = response.content
        bp_markdown = content.strip() if isinstance(content, str) else str(content)

    out_dir = Path(workspace) / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    fname = f"bp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    out_path = out_dir / fname
    out_path.write_text(bp_markdown, encoding="utf-8")

    rel_path = f"output/{fname}"
    print(f"[bp_simple] 已写入: {out_path}")

    return {"bp_markdown": bp_markdown, "bp_file_path": rel_path}

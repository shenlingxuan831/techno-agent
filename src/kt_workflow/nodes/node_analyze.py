"""kt_analyze — 大模型分析 extracted_text，写入 llm_source_analysis。"""

from __future__ import annotations

from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime

from coze_coding_utils.runtime_ctx.context import Context

from kt_workflow import constants as C
from kt_workflow.db.session import session_scope
from kt_workflow.repositories import artifacts as art_repo
from kt_workflow.repositories import runs as run_repo
from kt_workflow.services.source_analyzer import analyze_source_material
from kt_workflow.state import KTWorkflowState
from kt_workflow.nodes._helpers import safe_json_dumps


NODE_ID = "kt_analyze"


def kt_analyze_node(
    state: KTWorkflowState,
    config: RunnableConfig,
    runtime: Runtime[Context],
) -> dict:
    if not state.run_id:
        raise ValueError("kt_analyze: 缺少 run_id")

    with session_scope() as session:
        extracted = art_repo.get_latest_text(session, state.run_id, C.EXTRACTED_TEXT, "default") or ""
        analysis, meta = analyze_source_material(extracted, state)
        meta["node"] = NODE_ID
        run_repo.update_run_stage(session, state.run_id, "analyze")
        art_repo.write_artifact(
            session,
            state.run_id,
            C.LLM_SOURCE_ANALYSIS,
            "default",
            content_text=safe_json_dumps(analysis),
            meta_json=meta,
        )

    return {"current_stage": "analyze"}

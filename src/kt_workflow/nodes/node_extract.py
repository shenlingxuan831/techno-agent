"""kt_extract — 读入成果正文，写入 kt_artifacts（解析逻辑在 services/source_extract）。"""

from __future__ import annotations

from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime

from coze_coding_utils.runtime_ctx.context import Context

from kt_workflow import constants as C
from kt_workflow.db.session import session_scope
from kt_workflow.repositories import artifacts as art_repo
from kt_workflow.repositories import runs as run_repo
from kt_workflow.services.source_extract import extract_from_source_uri
from kt_workflow.state import KTWorkflowState


NODE_ID = "kt_extract"


def kt_extract_node(
    state: KTWorkflowState,
    config: RunnableConfig,
    runtime: Runtime[Context],
) -> dict:
    if not state.run_id:
        raise ValueError("kt_extract: 缺少 run_id，请确认 kt_ingest 已执行")
    text, extract_meta = extract_from_source_uri(state.source_uri)
    with session_scope() as session:
        run_repo.update_run_stage(session, state.run_id, "extract")
        art_repo.write_artifact(
            session,
            state.run_id,
            C.EXTRACTED_TEXT,
            "default",
            content_text=text,
            meta_json=extract_meta,
        )

    return {"current_stage": "extract"}

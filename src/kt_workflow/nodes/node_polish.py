"""kt_polish — 预览阶段直通整稿（不做 LLM 润色，便于查看组员原始产出）。"""

from __future__ import annotations

from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime

from coze_coding_utils.runtime_ctx.context import Context

from kt_workflow import constants as C
from kt_workflow.db.session import session_scope
from kt_workflow.repositories import artifacts as art_repo
from kt_workflow.repositories import runs as run_repo
from kt_workflow.state import KTWorkflowState


NODE_ID = "kt_polish"


def kt_polish_node(
    state: KTWorkflowState,
    config: RunnableConfig,
    runtime: Runtime[Context],
) -> dict:
    if not state.run_id:
        raise ValueError("缺少 run_id")

    with session_scope() as session:
        draft = art_repo.get_latest_text(session, state.run_id, C.BP_FULL_DRAFT, "default") or ""
        run_repo.update_run_stage(session, state.run_id, "polish")
        art_repo.write_artifact(
            session,
            state.run_id,
            C.BP_POLISHED,
            "default",
            content_text=draft,
            meta_json={"node": NODE_ID, "mode": "pass_through_for_preview"},
        )

    return {"current_stage": "polish"}

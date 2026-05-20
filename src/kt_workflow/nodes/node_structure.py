"""kt_structure — 将 extracted_text + llm_source_analysis 归并为 structured_profile。"""

from __future__ import annotations

from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime

from coze_coding_utils.runtime_ctx.context import Context

from kt_workflow import constants as C
from kt_workflow.db.session import session_scope
from kt_workflow.repositories import artifacts as art_repo
from kt_workflow.repositories import runs as run_repo
from kt_workflow.services.profile_builder import materialize_profile_for_run
from kt_workflow.state import KTWorkflowState
from kt_workflow.nodes._helpers import safe_json_dumps


NODE_ID = "kt_structure"


def kt_structure_node(
    state: KTWorkflowState,
    config: RunnableConfig,
    runtime: Runtime[Context],
) -> dict:
    if not state.run_id:
        raise ValueError("kt_structure: 缺少 run_id")
    with session_scope() as session:
        profile, meta = materialize_profile_for_run(session, state)
        run_repo.update_run_stage(session, state.run_id, "structure")
        art_repo.write_artifact(
            session,
            state.run_id,
            C.STRUCTURED_PROFILE,
            "default",
            content_text=safe_json_dumps(profile),
            meta_json=meta,
        )

    return {"current_stage": "structure"}

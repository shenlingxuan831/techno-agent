"""kt_ingest — 创建 project/run，写入来源元数据（框架桩）。"""

from __future__ import annotations

from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime

from coze_coding_utils.runtime_ctx.context import Context

from kt_workflow import constants as C
from kt_workflow.db.session import session_scope
from kt_workflow.repositories import artifacts as art_repo
from kt_workflow.repositories import runs as run_repo
from kt_workflow.state import KTWorkflowState


NODE_ID = "kt_ingest"


def kt_ingest_node(
    state: KTWorkflowState,
    config: RunnableConfig,
    runtime: Runtime[Context],
) -> dict:
    with session_scope() as session:
        project_id = (
            run_repo.create_project(session, state.project_name, id=state.project_id)
            if state.project_id
            else run_repo.create_project(session, state.project_name)
        )
        run_id = (
            run_repo.create_run(session, project_id, id=state.run_id)
            if state.run_id
            else run_repo.create_run(session, project_id)
        )
        run_repo.update_run_stage(session, run_id, "ingest")
        art_repo.write_artifact(
            session,
            run_id,
            C.SOURCE_META,
            "default",
            meta_json={
                "project_name": state.project_name,
                "source_uri": state.source_uri,
                "user_type": state.user_type,
                "contact_info": state.contact_info,
                "specific_requirements": state.specific_requirements,
            },
        )

    return {
        "project_id": project_id,
        "run_id": run_id,
        "current_stage": "ingest",
    }

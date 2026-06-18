"""kt_extract — 读入成果材料（PDF 三层：MinerU + 图目录 + 视觉），写入 kt_artifacts。"""

from __future__ import annotations

from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime

from coze_coding_utils.runtime_ctx.context import Context

from kt_workflow import constants as C
from kt_workflow.db.session import session_scope
from kt_workflow.nodes._helpers import safe_json_dumps
from kt_workflow.repositories import artifacts as art_repo
from kt_workflow.repositories import runs as run_repo
from kt_workflow.services.extract.figure_catalog import figures_to_json
from kt_workflow.services.source_extract import extract_from_source_uri, extract_meta_for_artifact
from kt_workflow.state import KTWorkflowState


NODE_ID = "kt_extract"


def kt_extract_node(
    state: KTWorkflowState,
    config: RunnableConfig,
    runtime: Runtime[Context],
) -> dict:
    if not state.run_id:
        raise ValueError("kt_extract: 缺少 run_id，请确认 kt_ingest 已执行")

    result = extract_from_source_uri(
        state.source_uri,
        run_id=state.run_id,
        project_name=state.project_name or "",
    )
    meta = extract_meta_for_artifact(result, state.source_uri)

    with session_scope() as session:
        run_repo.update_run_stage(session, state.run_id, "extract")

        art_repo.write_artifact(
            session,
            state.run_id,
            C.EXTRACTED_TEXT,
            "default",
            content_text=result.plain_text,
            meta_json=meta,
        )
        if result.markdown.strip():
            art_repo.write_artifact(
                session,
                state.run_id,
                C.EXTRACTED_MARKDOWN,
                "default",
                content_text=result.markdown,
                meta_json={**meta, "artifact_role": "structured_markdown"},
            )
        if result.figures:
            art_repo.write_artifact(
                session,
                state.run_id,
                C.SOURCE_FIGURES,
                "default",
                content_text=safe_json_dumps(figures_to_json(result.figures)),
                meta_json={"figure_count": len(result.figures), **meta},
            )
        if result.figure_analysis:
            art_repo.write_artifact(
                session,
                state.run_id,
                C.FIGURE_ANALYSIS,
                "default",
                content_text=safe_json_dumps(result.figure_analysis),
                meta_json=result.meta.get("vision", {}),
            )

    return {"current_stage": "extract"}

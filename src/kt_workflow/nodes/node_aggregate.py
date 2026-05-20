"""kt_aggregate — 按注册表顺序拼接全部 bp_module_*，生成完整 Markdown 草案。"""

from __future__ import annotations

from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime

from coze_coding_utils.runtime_ctx.context import Context

from kt_workflow import constants as C
from kt_workflow.db.session import session_scope
from kt_workflow.outline_loader import all_modules_in_order, load_registry
from kt_workflow.repositories import artifacts as art_repo
from kt_workflow.repositories import bp_modules
from kt_workflow.repositories import runs as run_repo
from kt_workflow.state import KTWorkflowState


NODE_ID = "kt_aggregate"


def kt_aggregate_node(
    state: KTWorkflowState,
    config: RunnableConfig,
    runtime: Runtime[Context],
) -> dict:
    if not state.run_id:
        raise ValueError("缺少 run_id")

    reg = load_registry()
    title = reg.get("document_title", "科技成果转化商业计划书")
    parts: list[str] = [f"# {title}\n"]

    with session_scope() as session:
        modules = list(all_modules_in_order())
        for mod in modules:
            mid = mod["id"]
            text = bp_modules.get_module_text(session, state.run_id, mid)
            if text:
                parts.append(text)
            chart = bp_modules.get_module_chart_json(session, state.run_id, mid)
            if chart:
                parts.append(
                    f"\n<!-- chart:{mid} ({mod.get('ref')}) -->\n"
                    f"```json\n{chart}\n```\n"
                )

        full_md = "\n\n".join(parts)
        run_repo.update_run_stage(session, state.run_id, "aggregate")
        art_repo.write_artifact(
            session,
            state.run_id,
            C.BP_FULL_DRAFT,
            "default",
            content_text=full_md,
            meta_json={"module_count": len(modules), "registry_version": reg.get("registry_version")},
        )

    return {"current_stage": "aggregate"}

"""按「章」调用 chapter_writers，写入 bp_module_text / bp_module_chart。

LangGraph 节点 `kt_chapter_00` … `kt_chapter_10` 均委托本模块；组员实现见
`kt_workflow/services/chapter_writers/chapter_XX.py`，勿在本文件写业务逻辑。
"""

from __future__ import annotations

import json

from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime

from coze_coding_utils.runtime_ctx.context import Context

from kt_workflow import constants as C
from kt_workflow.db.session import session_scope
from kt_workflow.outline_loader import load_registry, modules_for_chapter
from kt_workflow.repositories import artifacts as art_repo
from kt_workflow.repositories import bp_modules
from kt_workflow.repositories import runs as run_repo
from kt_workflow.services.chapter_writer_contract import ChapterWriterContext
from kt_workflow.services.chapter_writers import get_chapter_writer
from kt_workflow.state import KTWorkflowState


def _load_profile(session, run_id: str) -> dict:
    raw = art_repo.get_latest_text(session, run_id, C.STRUCTURED_PROFILE, "default")
    if not raw or not raw.strip():
        return {}
    try:
        parsed = json.loads(raw)
        return parsed if isinstance(parsed, dict) else {}
    except json.JSONDecodeError:
        return {}


def kt_chapter_runner(
    state: KTWorkflowState,
    config: RunnableConfig,
    runtime: Runtime[Context],
    chapter: int,
) -> dict:
    if not state.run_id:
        raise ValueError(f"chapter_{chapter}: 缺少 run_id")

    doc_title = load_registry().get("document_title", "BP")
    writer = get_chapter_writer(chapter)

    with session_scope() as session:
        run_repo.update_run_stage(session, state.run_id, f"chapter_{chapter}")
        profile = _load_profile(session, state.run_id)
        extracted = art_repo.get_latest_text(session, state.run_id, C.EXTRACTED_TEXT, "default")

        for mod in modules_for_chapter(chapter):
            ctx: ChapterWriterContext = {
                "run_id": state.run_id,
                "profile": profile,  # type: ignore[typeddict-item]
                "extracted_text": extracted,
                "module": mod,
                "document_title": doc_title,
            }
            markdown = writer.generate_module_text(ctx)
            bp_modules.write_module_text(
                session,
                state.run_id,
                mod,
                markdown,
                extra_meta={"writer_module": getattr(writer, "IMPLEMENTER_MODULE", "")},
            )
            if mod.get("needs_chart"):
                chart = writer.generate_module_chart(ctx)
                if chart:
                    bp_modules.write_module_chart_stub(
                        session,
                        state.run_id,
                        mod["id"],
                        str(mod.get("ref", "")),
                        spec=chart,
                    )
                else:
                    bp_modules.write_module_chart_stub(
                        session,
                        state.run_id,
                        mod["id"],
                        str(mod.get("ref", "")),
                    )

    return {"current_stage": f"chapter_{chapter}"}

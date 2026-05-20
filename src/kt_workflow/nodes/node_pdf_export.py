"""kt_pdf — 预览导出：生成 bp_preview.html（浏览器打开即可查看组员产出）。"""

from __future__ import annotations

import os

from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime

from coze_coding_utils.runtime_ctx.context import Context

from kt_workflow import constants as C
from kt_workflow.db.session import session_scope
from kt_workflow.outline_loader import load_registry
from kt_workflow.repositories import artifacts as art_repo
from kt_workflow.repositories import runs as run_repo
from kt_workflow.services.preview_builder import build_preview_html
from kt_workflow.state import KTWorkflowState
from kt_workflow.paths import kt_databases_dir, kt_run_output_dir


NODE_ID = "kt_pdf"


def kt_pdf_export_node(
    state: KTWorkflowState,
    config: RunnableConfig,
    runtime: Runtime[Context],
) -> dict:
    if not state.run_id:
        raise ValueError("缺少 run_id")

    out_dir = kt_run_output_dir(state.run_id)
    preview_html = out_dir / "bp_preview.html"
    mirror_md = out_dir / "bp_preview_source.md"

    reg = load_registry()
    doc_title = reg.get("document_title", "商业计划书")

    with session_scope() as session:
        polished = art_repo.get_latest_text(session, state.run_id, C.BP_POLISHED, "default") or ""
        run_repo.update_run_stage(session, state.run_id, "pdf", status="completed")

        mirror_md.write_text(polished, encoding="utf-8")
        html = build_preview_html(
            document_title=doc_title,
            markdown_body=polished,
            run_id=state.run_id,
            project_name=state.project_name or "",
        )
        preview_html.write_text(html, encoding="utf-8")

        html_uri = str(preview_html.resolve())
        sqlite_path = ""
        if not (os.getenv("KT_WORKFLOW_DATABASE_URL") or "").strip():
            sqlite_path = str((kt_databases_dir() / f"{state.run_id}.sqlite").resolve())

        art_repo.write_artifact(
            session,
            state.run_id,
            C.PDF_EXPORT,
            "default",
            content_text=f"HTML preview:\n- html: {preview_html}\n- md: {mirror_md}\n",
            storage_uri=html_uri,
            meta_json={
                "format": "html_preview",
                "note": "预览用 HTML；正式 PDF 由负责人另行渲染",
            },
        )

    summary = {
        "preview_html_path": html_uri,
        "preview_markdown_path": str(mirror_md.resolve()),
        "run_output_dir": str(out_dir.resolve()),
        "database": "kt_artifacts.pdf_export storage_uri points to HTML preview",
    }
    if sqlite_path:
        summary["sqlite_path"] = sqlite_path

    return {
        "current_stage": "pdf",
        "summary": summary,
    }

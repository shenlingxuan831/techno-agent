"""BP 细粒度模块写入：正文与图表用同一 module id（slug）关联。"""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from kt_workflow import constants as C
from kt_workflow.repositories import artifacts as art_repo
from kt_workflow.outline_loader import BpModuleSpec
from kt_workflow.nodes._helpers import safe_json_dumps


def write_module_text(
    session: Session,
    run_id: str,
    module: BpModuleSpec,
    content_markdown: str,
    extra_meta: dict[str, Any] | None = None,
) -> str:
    meta = {
        "ref": module.get("ref"),
        "title": module.get("title"),
        "chapter": module.get("chapter"),
        "kind": "bp_module_text",
    }
    wh = module.get("writer_hint")
    if wh:
        meta["writer_hint"] = wh
    if extra_meta:
        meta.update(extra_meta)
    return art_repo.write_artifact(
        session,
        run_id,
        C.BP_MODULE_TEXT,
        module["id"],
        content_text=content_markdown,
        meta_json=meta,
    )


def write_module_chart_stub(
    session: Session,
    run_id: str,
    module_id: str,
    module_ref: str,
    spec: dict[str, Any] | None = None,
) -> str:
    payload = spec or {
        "module_id": module_id,
        "ref": module_ref,
        "type": "placeholder",
        "note": "实现时写入真实 chart spec 与渲染文件 storage_uri",
    }
    return art_repo.write_artifact(
        session,
        run_id,
        C.BP_MODULE_CHART,
        module_id,
        content_text=safe_json_dumps(payload),
        meta_json={"kind": "bp_module_chart", "pairs_with_text_slug": module_id},
    )


def get_module_text(session: Session, run_id: str, module_id: str) -> str | None:
    return art_repo.get_latest_text(session, run_id, C.BP_MODULE_TEXT, module_id)


def get_module_chart_json(session: Session, run_id: str, module_id: str) -> str | None:
    return art_repo.get_latest_text(session, run_id, C.BP_MODULE_CHART, module_id)

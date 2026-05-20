from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from kt_workflow.models.tables import KtProject, KtWorkflowRun


def create_project(session: Session, name: str, id: str | None = None) -> str:
    if id:
        p = KtProject(id=id, name=name or "未命名项目")
    else:
        p = KtProject(name=name or "未命名项目")
    session.add(p)
    session.flush()
    return p.id


def create_run(session: Session, project_id: str, id: str | None = None) -> str:
    if id:
        r = KtWorkflowRun(id=id, project_id=project_id, status="running", stage="init")
    else:
        r = KtWorkflowRun(project_id=project_id, status="running", stage="init")
    session.add(r)
    session.flush()
    return r.id


def update_run_stage(session: Session, run_id: str, stage: str, status: str | None = None) -> None:
    r = session.get(KtWorkflowRun, run_id)
    if not r:
        return
    r.stage = stage
    r.updated_at = datetime.now(timezone.utc)
    if status is not None:
        r.status = status


def get_run_project_id(session: Session, run_id: str) -> str | None:
    r = session.get(KtWorkflowRun, run_id)
    return r.project_id if r else None

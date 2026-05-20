from __future__ import annotations

from typing import Any, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from kt_workflow.models.tables import KtArtifact


def _next_version(session: Session, run_id: str, artifact_type: str, slug: str) -> int:
    stmt = select(func.coalesce(func.max(KtArtifact.version), 0)).where(
        KtArtifact.run_id == run_id,
        KtArtifact.artifact_type == artifact_type,
        KtArtifact.slug == slug,
    )
    current = session.scalar(stmt)
    return int(current or 0) + 1


def write_artifact(
    session: Session,
    run_id: str,
    artifact_type: str,
    slug: str = "default",
    content_text: str | None = None,
    storage_uri: str | None = None,
    meta_json: dict[str, Any] | None = None,
) -> str:
    ver = _next_version(session, run_id, artifact_type, slug)
    row = KtArtifact(
        run_id=run_id,
        artifact_type=artifact_type,
        slug=slug,
        content_text=content_text,
        storage_uri=storage_uri,
        meta_json=meta_json,
        version=ver,
    )
    session.add(row)
    session.flush()
    return row.id


def get_latest_text(
    session: Session,
    run_id: str,
    artifact_type: str,
    slug: str = "default",
) -> Optional[str]:
    stmt = (
        select(KtArtifact.content_text)
        .where(
            KtArtifact.run_id == run_id,
            KtArtifact.artifact_type == artifact_type,
            KtArtifact.slug == slug,
        )
        .order_by(KtArtifact.version.desc())
        .limit(1)
    )
    return session.scalar(stmt)


def get_latest_meta(
    session: Session,
    run_id: str,
    artifact_type: str,
    slug: str = "default",
) -> Optional[dict[str, Any]]:
    stmt = (
        select(KtArtifact.meta_json)
        .where(
            KtArtifact.run_id == run_id,
            KtArtifact.artifact_type == artifact_type,
            KtArtifact.slug == slug,
        )
        .order_by(KtArtifact.version.desc())
        .limit(1)
    )
    return session.scalar(stmt)

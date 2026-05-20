from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from kt_workflow.db.base import KtBase


def _uuid() -> str:
    return str(uuid.uuid4())


class KtProject(KtBase):
    __tablename__ = "kt_projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(512), default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    runs: Mapped[list["KtWorkflowRun"]] = relationship(back_populates="project")


class KtWorkflowRun(KtBase):
    __tablename__ = "kt_workflow_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    project_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("kt_projects.id", ondelete="CASCADE"),
        index=True,
    )
    status: Mapped[str] = mapped_column(String(64), default="running")
    stage: Mapped[str] = mapped_column(String(64), default="init")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    project: Mapped["KtProject"] = relationship(back_populates="runs")
    artifacts: Mapped[list["KtArtifact"]] = relationship(back_populates="run")


class KtArtifact(KtBase):
    """Append-only versioned blobs: latest row wins per (run_id, artifact_type, slug)."""

    __tablename__ = "kt_artifacts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    run_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("kt_workflow_runs.id", ondelete="CASCADE"),
        index=True,
    )
    artifact_type: Mapped[str] = mapped_column(String(128), index=True)
    slug: Mapped[str] = mapped_column(String(128), default="default", index=True)
    content_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    storage_uri: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    meta_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    run: Mapped["KtWorkflowRun"] = relationship(back_populates="artifacts")

"""Engine and session factory for kt_workflow (separate from Coze PG stack)."""

from __future__ import annotations

import os
from contextlib import contextmanager
from contextvars import ContextVar
from pathlib import Path
from typing import Generator, Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from kt_workflow.paths import kt_databases_dir

_engine: Optional[Engine] = None
_session_factory: Optional[sessionmaker] = None

_sqlite_run_id: ContextVar[Optional[str]] = ContextVar("kt_workflow_sqlite_run_id", default=None)


def bind_sqlite_run(run_id: str) -> None:
    """将当前异步任务绑到独立 SQLite 文件 ``databases/<run_id>.sqlite``。

    若已设置 ``KT_WORKFLOW_DATABASE_URL``（如 Postgres），则不做任何事。
    """
    if (os.getenv("KT_WORKFLOW_DATABASE_URL") or "").strip():
        return
    reset_engine_for_tests()
    _sqlite_run_id.set(run_id)


def clear_sqlite_run_binding() -> None:
    _sqlite_run_id.set(None)
    reset_engine_for_tests()


def _default_sqlite_url() -> str:
    run_id = _sqlite_run_id.get()
    db_dir = kt_databases_dir()
    if run_id:
        path = db_dir / f"{run_id}.sqlite"
    else:
        path = db_dir / "kt_workflow.sqlite3"
    return f"sqlite:///{path.as_posix()}"


def get_database_url() -> str:
    url = (os.getenv("KT_WORKFLOW_DATABASE_URL") or "").strip()
    if url:
        return url
    return _default_sqlite_url()


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = create_engine(
            get_database_url(),
            pool_pre_ping=True,
            echo=os.getenv("KT_WORKFLOW_SQL_ECHO", "").strip() in ("1", "true", "yes"),
        )
    return _engine


def get_session_factory() -> sessionmaker:
    global _session_factory
    if _session_factory is None:
        _session_factory = sessionmaker(
            bind=get_engine(),
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        )
    return _session_factory


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    factory = get_session_factory()
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def reset_engine_for_tests() -> None:
    """Optional: call between tests to switch URL."""
    global _engine, _session_factory
    _engine = None
    _session_factory = None

from kt_workflow.db.base import KtBase
from kt_workflow.db.session import get_engine


def ensure_schema() -> None:
    """Create kt_* tables if missing (dev-friendly; production may use Alembic later)."""
    import kt_workflow.models.tables  # noqa: F401 — register mappers

    KtBase.metadata.create_all(bind=get_engine())

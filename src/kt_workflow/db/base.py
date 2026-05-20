from sqlalchemy.orm import DeclarativeBase


class KtBase(DeclarativeBase):
    """SQLAlchemy base for kt_workflow tables only (isolated from storage/database/shared)."""

    pass

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import JSON, DateTime, Float, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from src.infrastructure.retry import with_exponential_backoff
from src.infrastructure.settings import get_settings


class Base(DeclarativeBase):
    pass


class PredictionRecord(Base):
    __tablename__ = "wafer_predictions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    label: Mapped[str] = mapped_column(String(16), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    raw_prediction: Mapped[int] = mapped_column(nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    source: Mapped[str] = mapped_column(String(32), nullable=False, default="api")


def get_engine():
    settings = get_settings()
    return create_engine(settings.sqlalchemy_db_uri, pool_pre_ping=True)


def init_db() -> None:
    engine = get_engine()
    Base.metadata.create_all(bind=engine)


def _insert_record(record: PredictionRecord) -> None:
    engine = get_engine()
    session_maker = sessionmaker(bind=engine)
    with session_maker() as session:
        session.add(record)
        session.commit()


def save_prediction(payload: dict[str, Any], label: str, confidence: float, raw_prediction: int, source: str) -> None:
    record = PredictionRecord(
        payload=payload,
        label=label,
        confidence=confidence,
        raw_prediction=raw_prediction,
        source=source,
    )
    with_exponential_backoff(_insert_record, record, retries=3)

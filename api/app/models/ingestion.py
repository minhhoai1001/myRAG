# app/models/ingestion.py
from sqlalchemy import String, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from uuid import uuid4
from app.db import Base

class IngestionJob(Base):
    __tablename__ = "ingestion_job"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    document_id: Mapped[str] = mapped_column(String, ForeignKey("document.id", ondelete="CASCADE"), nullable=False)
    stage: Mapped[str] = mapped_column(String, nullable=False)  # queued|downloading|parsing|chunking|embedding|upserting|completed|failed
    detail: Mapped[str | None] = mapped_column(String)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())

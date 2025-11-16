# app/models/document.py
from sqlalchemy import String, DateTime, func, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from uuid import uuid4
from app.db import Base

class Document(Base):
    __tablename__ = "document"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    knowledge_id: Mapped[str] = mapped_column(String, ForeignKey("knowledge.id", ondelete="CASCADE"), nullable=False)
    filename: Mapped[str] = mapped_column(String, nullable=False)
    s3_key: Mapped[str] = mapped_column(String, nullable=False)
    uploaded_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    page_count: Mapped[int | None] = mapped_column(Integer)
    chunk_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String, nullable=False, default="uploaded")  # uploaded|ingesting|ready|error

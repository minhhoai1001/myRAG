# app/models/chunk.py
from sqlalchemy import String, DateTime, func, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from uuid import uuid4
from app.db import Base

class Chunk(Base):
    __tablename__ = "chunk"
    __table_args__ = (
        UniqueConstraint("document_id", "chunk_index", name="uq_chunk_doc_idx"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    document_id: Mapped[str] = mapped_column(String, ForeignKey("document.id", ondelete="CASCADE"), nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    section: Mapped[str | None] = mapped_column(String)
    page_from: Mapped[int | None] = mapped_column(Integer)
    page_to: Mapped[int | None] = mapped_column(Integer)
    token_count: Mapped[int | None] = mapped_column(Integer)
    text_hash: Mapped[str | None] = mapped_column(String)
    vector_id: Mapped[str | None] = mapped_column(String)  # id trong vector DB (Qdrant/Milvus)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())

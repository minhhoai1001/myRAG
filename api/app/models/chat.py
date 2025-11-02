# app/models/chat.py
from sqlalchemy import String, DateTime, func, ForeignKey, CheckConstraint, JSON
from sqlalchemy.orm import Mapped, mapped_column
from uuid import uuid4
from app.db import Base

class ChatSession(Base):
    __tablename__ = "chat_session"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    knowledge_id: Mapped[str] = mapped_column(String, ForeignKey("knowledge.id", ondelete="CASCADE"), nullable=False)
    owner_id: Mapped[str | None] = mapped_column(String, ForeignKey("users.id", ondelete="SET NULL"))
    section: Mapped[str | None] = mapped_column(String)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())

class ChatMessage(Base):
    __tablename__ = "chat_message"
    __table_args__ = (
        CheckConstraint("role IN ('user','assistant','system')", name="ck_chat_message_role"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    session_id: Mapped[str] = mapped_column(String, ForeignKey("chat_session.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    retrieval_context: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # JSONB in PostgreSQL
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.deps import get_db
from app.models import ChatSession, ChatMessage, Knowledge
from app.schemas import ChatIn
from app.services.qdrant import search_chunks
import uuid, datetime as dt

router = APIRouter()

@router.post("/knowledge/{kid}/chat/sessions")
def create_session(kid: str, body: ChatIn, db: Session = Depends(get_db)):
    if not db.get(Knowledge, kid): raise HTTPException(404, "Knowledge not found")
    sid = str(uuid.uuid4())
    sess = ChatSession(id=sid, knowledge_id=kid, section=body.section)
    db.add(sess); db.commit()
    return {"session_id": sid}

@router.get("/chat/sessions/{sid}/messages")
def list_messages(sid: str, db: Session = Depends(get_db)):
    from app.models import ChatMessage
    msgs = db.query(ChatMessage).filter(ChatMessage.session_id == sid).order_by(ChatMessage.created_at.asc()).all()
    return [{"role": m.role, "content": m.content, "created_at": m.created_at, "retrieval_context": m.retrieval_context} for m in msgs]

@router.post("/chat/sessions/{sid}/messages")
def chat_send(sid: str, body: ChatIn, db: Session = Depends(get_db)):
    sess = db.get(ChatSession, sid)
    if not sess: raise HTTPException(404, "Session not found")
    # save user msg
    um = ChatMessage(id=str(uuid.uuid4()), session_id=sid, role="user", content=body.content)
    db.add(um); db.flush()
    # retrieve
    hits = search_chunks(sess.knowledge_id, body.content, sess.section, top_k=6)
    # (placeholder) gọi LLM ở đây, dùng hits để làm context → answer
    answer = f"(demo) Top {len(hits)} chunks retrieved."
    am = ChatMessage(
        id=str(uuid.uuid4()),
        session_id=sid,
        role="assistant",
        content=answer,
        retrieval_context=hits,
    )
    db.add(am); db.commit()
    return {"answer": answer, "sources": hits}

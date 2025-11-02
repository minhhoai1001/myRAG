from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.deps import get_db
from app.models import Document, Knowledge
from app.schemas import PresignIn, DocOut
from app.services.s3_presign import make_s3_key, presign_put_url, BUCKET
import uuid, datetime as dt

router = APIRouter()

@router.post("/knowledge/{kid}/documents/upload-url")
def get_upload_url(kid: str, body: PresignIn, db: Session = Depends(get_db)):
    if not db.get(Knowledge, kid): raise HTTPException(404, "Knowledge not found")
    doc_id = str(uuid.uuid4())
    key = make_s3_key(kid, doc_id, body.filename)
    url = presign_put_url(BUCKET, key, body.content_type)
    doc = Document(id=doc_id, knowledge_id=kid, filename=body.filename, s3_key=key, status="uploaded")
    db.add(doc); db.commit()
    return {"doc_id": doc_id, "upload_url": url, "s3_key": key}

@router.get("/knowledge/{kid}/documents", response_model=list[DocOut])
def list_docs(kid: str, db: Session = Depends(get_db)):
    q = db.query(Document).filter(Document.knowledge_id == kid).order_by(Document.uploaded_at.desc())
    return q.all()

@router.post("/documents/{doc_id}/ingest")
def trigger_ingest(doc_id: str, db: Session = Depends(get_db)):
    doc = db.get(Document, doc_id)
    if not doc: raise HTTPException(404, "Document not found")
    # TODO: push message to queue (Redis/Kafka). Tạm thời đặt status
    doc.status = "ingesting"; db.commit()
    return {"queued": True, "doc_id": doc_id}

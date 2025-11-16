from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.deps import get_db
from app.models import Document, Knowledge
from app.schemas import PresignIn, DocOut
from app.services.s3_presign import make_s3_key, presign_put_url, presign_delete_url, BUCKET
import uuid, datetime as dt

router = APIRouter()

@router.post("/knowledge/{kid}/documents/upload-url")
def get_upload_url(kid: str, knowledge_name: str, body: PresignIn, db: Session = Depends(get_db)):
    knowledge = db.get(Knowledge, kid)
    if not knowledge:
        raise HTTPException(status_code=404, detail="Knowledge not found")

    # Check if document with same filename already exists
    existing_doc = db.query(Document).filter(
        Document.knowledge_id == kid,
        Document.filename == body.filename
    ).order_by(Document.uploaded_at.desc()).first()

    if existing_doc:
        # Use existing doc_id and update the document
        doc_id = existing_doc.id
        key = make_s3_key(knowledge_name, doc_id)
        
        # Update existing document
        existing_doc.s3_key = f"s3://{BUCKET}/{key}"
        existing_doc.status = "uploaded"
        existing_doc.chunk_count = 0  # Reset chunk count when replacing
        existing_doc.page_count = None  # Reset page count when replacing
        
        url = presign_put_url(key, body.content_type)
        
        try:
            db.flush()
            db.commit()
            db.refresh(existing_doc)
            print(f"Updated existing document: id={doc_id}, filename={existing_doc.filename}, status={existing_doc.status}")
        except Exception as e:
            db.rollback()
            print(f"Error updating document in database: {e}")
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Failed to update document: {str(e)}")
    else:
        # Create new document
        doc_id = str(uuid.uuid4())
        key = make_s3_key(knowledge_name, doc_id)
        
        url = presign_put_url(key, body.content_type)
        
        try:
            doc = Document(
                id=doc_id,
                knowledge_id=kid,
                filename=body.filename,
                s3_key=f"s3://{BUCKET}/{key}",
                status="uploaded",
            )
            db.add(doc)
            db.flush()
            db.commit()
            db.refresh(doc)
            print(f"Generated presigned URL for bucket='{BUCKET}', key='{key}', doc_id='{doc_id}'")
            print(f"Document saved: id={doc.id}, filename={doc.filename}, status={doc.status}")
        except Exception as e:
            db.rollback()
            print(f"Error saving document to database: {e}")
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Failed to save document: {str(e)}")

    return {
        "doc_id": doc_id,
        "upload_url": url,
        "s3_key": key,
        "bucket": BUCKET,
    }

@router.get("/knowledge/{kid}/documents", response_model=list[DocOut])
def list_docs(kid: str, db: Session = Depends(get_db)):
    q = db.query(Document).filter(Document.knowledge_id == kid).order_by(Document.uploaded_at.desc())
    return q.all()

@router.get("/documents/{doc_id}/delete-url")
def get_delete_url(doc_id: str, db: Session = Depends(get_db)):
    doc = db.get(Document, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Extract S3 key from s3_key (format: s3://bucket/key)
    s3_key = doc.s3_key
    if s3_key.startswith(f"s3://{BUCKET}/"):
        key = s3_key.replace(f"s3://{BUCKET}/", "")
    else:
        # Fallback: try to extract key from s3_key
        key = s3_key.split("/", 3)[-1] if "/" in s3_key else s3_key
    
    try:
        delete_url = presign_delete_url(key)
        return {
            "doc_id": doc_id,
            "delete_url": delete_url,
            "s3_key": key,
            "bucket": BUCKET,
        }
    except Exception as e:
        print(f"Error generating delete URL: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to generate delete URL: {str(e)}")

@router.post("/documents/{doc_id}/ingest")
def trigger_ingest(doc_id: str, db: Session = Depends(get_db)):
    doc = db.get(Document, doc_id)
    if not doc:
        raise HTTPException(404, "Document not found")
    try:
        # TODO: push message to queue (Redis/Kafka). Tạm thời đặt status
        doc.status = "ingesting"
        db.flush()
        db.commit()
        db.refresh(doc)
        return {"queued": True, "doc_id": doc_id}
    except Exception as e:
        db.rollback()
        print(f"Error updating document status: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to update document status: {str(e)}")

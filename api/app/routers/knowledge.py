from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.deps import get_db
from app.models import Knowledge
from app.schemas import KnowledgeCreate, KnowledgeOut
import uuid

router = APIRouter()

@router.get("/knowledge", response_model=list[KnowledgeOut])
def list_knowledge(db: Session = Depends(get_db)):
    return db.query(Knowledge).order_by(Knowledge.created_at.desc()).all()

@router.post("/knowledge", response_model=KnowledgeOut)
def create_knowledge(body: KnowledgeCreate, db: Session = Depends(get_db)):
    k = Knowledge(id=str(uuid.uuid4()), name=body.name, description=body.description)
    db.add(k); db.commit(); db.refresh(k)
    return k

@router.get("/knowledge/{kid}", response_model=KnowledgeOut)
def get_knowledge(kid: str, db: Session = Depends(get_db)):
    k = db.get(Knowledge, kid)
    if not k: raise HTTPException(404, "Not found")
    return k

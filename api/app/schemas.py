from pydantic import BaseModel
from typing import Optional

class KnowledgeCreate(BaseModel):
    name: str
    description: Optional[str] = None

class KnowledgeOut(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    class Config: from_attributes = True

class PresignIn(BaseModel):
    filename: str
    content_type: str

class DocOut(BaseModel):
    id: str
    filename: str
    chunk_count: int
    class Config: from_attributes = True

class ChatIn(BaseModel):
    content: str
    section: Optional[str] = None

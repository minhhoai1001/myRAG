from fastapi import FastAPI
from app.routers import knowledge, documents, chat
app = FastAPI(title="RAG API")
# Register more specific routes first to avoid conflicts
app.include_router(documents.router, prefix="/api", tags=["documents"])
app.include_router(knowledge.router, prefix="/api", tags=["knowledge"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])

@app.get("/health")
def health(): return {"ok": True}

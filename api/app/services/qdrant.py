import os, numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue

client = QdrantClient(url=os.getenv("QDRANT_URL", "http://localhost:6333"))
VECTOR_SIZE = 1024

def embed_query(text: str) -> list[float]:
    v = np.random.randn(VECTOR_SIZE).astype(np.float32); v /= (np.linalg.norm(v)+1e-12)
    return v.tolist()

def search_chunks(knowledge_id: str, query: str, section: str | None, top_k: int = 8):
    v = embed_query(query)
    must = [FieldCondition(key="knowledge_id", match=MatchValue(value=knowledge_id))]
    if section: must.append(FieldCondition(key="section", match=MatchValue(value=section)))
    flt = Filter(must=must)
    res = client.search("rag_chunks", query_vector=v, query_filter=flt, limit=top_k, with_payload=True)
    return [{"chunk_id": r.id, "score": r.score, **(r.payload or {})} for r in res]

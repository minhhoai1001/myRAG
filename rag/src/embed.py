import os
import ollama
import numpy as np

class Embed:
    def __init__(self, model: str = "qwen3-embedding:0.6b"):
        self.model = model
        self.host = os.getenv("OLLAMA_HOST", "http://host.docker.internal:11434")
        self.client = ollama.Client(host=self.host)

    def embed(self, text: str) -> np.ndarray:
        embedding = self.client.embeddings(model=self.model, prompt=text)
        return np.array(embedding["embedding"])

    def embed_batch(self, texts: list[str]) -> list[np.ndarray]:
        embeddings = []
        for text in texts:
            embedding = self.client.embeddings(model=self.model, prompt=text)
            embeddings.append(np.array(embedding["embedding"]))
        return embeddings

if __name__ == "__main__":
    from vectorstore import QdrantVectorStore
    qdrant = QdrantVectorStore(host=os.getenv("QDRANT_HOST", "qdrant"), port=os.getenv("QDRANT_PORT", 6333))
    embed = Embed()
    embeddings = embed.embed_batch(["Hello, world!", "Hello, world!"])
    # qdrant.insert_emb(collection_name="simpleRAG", embeddings=embedding, payloads={"text": "Hello, world!"})
    print(embeddings)
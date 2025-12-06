from qdrant_client import QdrantClient, models
from qdrant_client.models import Distance, VectorParams, PointStruct
from typing import List, Optional, Dict, Any
import numpy as np
import uuid


class QdrantVectorStore:
    """Class for managing Qdrant vector database operations"""
    
    def __init__(self, host: str = "localhost", port: int = 6333, vector_size: int = 1024):
        """
        Initialize Qdrant client and collection
        
        Args:
            host: Qdrant server host
            port: Qdrant server port
            collection_name: Name of the collection
            vector_size: Dimension of the vectors (default: 1024)
        """
        self.client = QdrantClient(host=host, port=port)
        self.vector_size = vector_size
    
    def _create_collection(self, collection_name: str):
        """Create collection if it doesn't exist"""
        if not self.client.collection_exists(collection_name):
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE
                )
            )
            print(f"✅ Created collection '{collection_name}' with vector size {self.vector_size}")
        else:
            print(f"✅ Collection '{collection_name}' already exists")
    
    def insert_emb(
        self,
        collection_name: str,
        embeddings: Optional[np.ndarray|list] = None,
        payloads: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Insert embeddings into the collection
        
        Args:
            embeddings: numpy array of embeddings (shape: [n, vector_size])
            payloads: Optional list of payload dictionaries (metadata for each embedding)
            ids: Optional list of point IDs. If None, auto-generate UUIDs
        
        Returns:
            True if successful
        """
        try:
            self._create_collection(collection_name)
            if isinstance(payloads, list):
                num_vectors = len(payloads)
                points = [
                    PointStruct(
                        id=uuid.uuid4(),
                        vector=embeddings[i],
                        payload=payloads[i]
                    )
                    for i in range(num_vectors)
                ]
            else:
                # Create points
                points = [
                    PointStruct(
                        id=uuid.uuid4(),
                        vector=embeddings,
                        payload=payloads
                    )
                ]
            
            # Insert points
            self.client.upsert(
                collection_name=collection_name,
                points=points
            )
            
            print(f"✅ Inserted embeddings into collection '{collection_name}'")
            return True
            
        except Exception as e:
            print(f"❌ Error inserting embeddings: {str(e)}")
            return False
    
    def search(
        self,
        collection_name: str,
        query_embedding: Optional[np.ndarray | list] = None,
        top_k: int = 5,
        score_threshold: Optional[float] = None,
        filter_conditions: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors in the collection
        
        Args:
            query_embedding: Query embedding vector as numpy array or list (shape: [vector_size] or [1, vector_size])
            top_k: Number of top results to return
            score_threshold: Minimum similarity score threshold
            filter_conditions: Optional filter conditions for payload
        
        Returns:
            List of search results, each containing 'id', 'score', and 'payload'
        """
        try:
            # Convert numpy array to list
            if isinstance(query_embedding, np.ndarray):
                # Handle both 1D and 2D arrays
                if query_embedding.ndim == 2:
                    query_vector = query_embedding[0].tolist()
                else:
                    query_vector = query_embedding.tolist()
            else:
                query_vector = query_embedding
            
            # Build search parameters
            search_params = {
                "collection_name": collection_name,
                "query_vector": query_vector,
                "limit": top_k
            }
            
            if score_threshold is not None:
                search_params["score_threshold"] = score_threshold
            
            if filter_conditions is not None:
                search_params["query_filter"] = models.Filter(**filter_conditions)
            
            # Perform search
            results = self.client.search(**search_params)
            
            # Format results
            formatted_results = [
                {
                    "id": result.id,
                    "score": result.score,
                    "payload": result.payload
                }
                for result in results
            ]
            
            return formatted_results
            
        except Exception as e:
            print(f"❌ Error searching: {str(e)}")
            return []
    
    def delete_collection(self, collection_name: str):
        """Delete the collection"""
        try:
            self.client.delete_collection(collection_name)
            print(f"✅ Deleted collection '{collection_name}'")
        except Exception as e:
            print(f"❌ Error deleting collection: {str(e)}")
    
    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """Get information about the collection"""
        try:
            info = self.client.get_collection(collection_name)
            return {
                "name": collection_name,
                "vectors_count": getattr(info, "points_count", None),
                "vector_size": getattr(info.config.params.vectors, "size", None),
                "distance": getattr(info.config.params.vectors, "distance", None)
            }
        except Exception as e:
            print(f"❌ Error getting collection info: {str(e)}")
            return {}

    def delete_document(self, collection_name: str, doc_id: str):
        """Delete all points that have file_name in payload from the collection"""
        try:
            self.client.delete(
                collection_name=collection_name,
                points_selector=models.FilterSelector(
                    filter=models.Filter(
                        must=[
                            models.FieldCondition(
                                key="doc_id",
                                match=models.MatchValue(value=doc_id)
                            )
                        ]
                    )
                )
            )
            print(f"✅ Deleted all points with doc_id '{doc_id}' from collection '{collection_name}'")
        except Exception as e:
            print(f"❌ Error deleting document: {str(e)}")


# Example usage
if __name__ == "__main__":
    # Initialize Qdrant vector store
    vector_store = QdrantVectorStore(
        vector_size=1024
    )
    
    # Get collection info
    info = vector_store.get_collection_info(collection_name="simpleRAG")
    print(f"Collection info: {info}")

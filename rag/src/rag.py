import os
import time
import logging
import boto3
import requests
from botocore.exceptions import ClientError
from semantic_text_splitter import MarkdownSplitter
from docling.document_converter import DocumentConverter

from .embed import Embed
from .vectorstore import QdrantVectorStore

logger = logging.getLogger('rag_worker.rag')

class ChunkingRAG:
    def __init__(self):
        self.s3_client = boto3.client(
            's3', 
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"), 
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"), 
            region_name=os.getenv("AWS_REGION", "ap-northeast-1")
        )
        self.document_converter = DocumentConverter()
        self.splitters = MarkdownSplitter.from_tiktoken_model("gpt-4o", capacity=(800, 1000), overlap=100)
        self.embed = Embed(model="qwen3-embedding:0.6b")
        self.qdrant = QdrantVectorStore(host=os.getenv("QDRANT_HOST", "qdrant"), port=os.getenv("QDRANT_PORT", 6333))

    def get_s3_object(self, s3_path: str):
        if s3_path.startswith("s3://"):
            parts = s3_path.replace("s3://", "").split("/", 1)
        else:
            parts = s3_path.split("/", 1)

        bucket = parts[0]
        key = parts[1] if len(parts) > 1 else ""

        return bucket, key

    def s3_object_exists(self, bucket: str, key: str) -> bool:
        """Check if S3 object exists"""
        try:
            self.s3_client.head_object(Bucket=bucket, Key=key)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            raise

    def download_document(self, s3_key: str, file_name: str, max_retries: int = 5, retry_delay: int = 2):
        save_path = os.path.join("/app", "tmp", file_name)
        bucket, key = self.get_s3_object(s3_key)
        logger.info(f"Downloading document from s3://{bucket}/{key} to {save_path}")
        
        # Wait for file to be available in S3 (with retry)
        for attempt in range(max_retries):
            if self.s3_object_exists(bucket, key):
                logger.debug(f"File found in S3 on attempt {attempt + 1}")
                break
            if attempt < max_retries - 1:
                logger.warning(f"File not found in S3, retrying in {retry_delay} seconds... (attempt {attempt + 1}/{max_retries})")
                time.sleep(retry_delay)
            else:
                error_msg = f"File not found in S3 after {max_retries} attempts: s3://{bucket}/{key}"
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)
        
        self.s3_client.download_file(bucket, key, save_path)
        logger.info(f"Document downloaded successfully to {save_path}")
        return save_path

    def convert_document(self, document_path: str):
        result = self.document_converter.convert(document_path)
        return result.document

    def upload_document(self, message: dict):
        doc_id = message.get('id')
        knowledge_id = message.get('knowledge_id')
        file_name = message.get('filename')
        s3_key = message.get('s3_key')
        
        logger.info(f"Starting document ingestion - Doc ID: {doc_id}, Knowledge ID: {knowledge_id}, File: {file_name}, S3 Key: {s3_key}")
        
        try:
            doc_path = self.download_document(s3_key, file_name)
            logger.info(f"Document downloaded successfully: {doc_path}")
            
            logger.debug("Converting document...")
            document = self.convert_document(doc_path)
            
            logger.debug("Splitting document into chunks...")
            chunks = self.splitters.chunks(document.export_to_markdown())
            logger.info(f"Document split into {len(chunks)} chunks")
            
            logger.debug("Processing chunks and generating embeddings...")
            for i, chunk in enumerate(chunks):
                embedding = self.embed.embed(chunk)
                payload = {
                    "doc_id": doc_id,
                    "text": chunk,
                    'file_name': file_name,
                    'chunk_index': i
                }
                self.qdrant.insert_emb(collection_name=knowledge_id, embeddings=embedding, payloads=payload)
                if (i + 1) % 10 == 0:
                    logger.debug(f"Processed {i + 1}/{len(chunks)} chunks")
            
            logger.info(f"All chunks processed and inserted into vector store for document {doc_id}")
            
            try:
                logger.debug(f"Updating document status to 'ready' for document {doc_id}")
                requests.patch(f"http://api:8000/api/documents/{doc_id}", json={"chunk_count": len(chunks), "status": "ready"})
                logger.info(f"Document {doc_id} successfully ingested with {len(chunks)} chunks")
            except Exception as e:
                logger.error(f"Error updating document status to 'ready': {e}", exc_info=True)
                return False
            return True
        except FileNotFoundError as e:
            # File not found in S3 after retries
            error_msg = str(e)
            logger.error(f"File not found error during document upload: {error_msg}")
            try:
                requests.patch(f"http://api:8000/api/documents/{doc_id}", json={"status": "error"})
                logger.info(f"Updated document {doc_id} status to 'error'")
            except Exception as update_error:
                logger.error(f"Error updating document status to 'error': {update_error}", exc_info=True)
            return False
        except Exception as e:
            # Other errors during processing
            error_msg = str(e)
            logger.error(f"Error during document upload: {error_msg}", exc_info=True)
            try:
                requests.patch(f"http://api:8000/api/documents/{doc_id}", json={"status": "error"})
                logger.info(f"Updated document {doc_id} status to 'error'")
            except Exception as update_error:
                logger.error(f"Error updating document status to 'error': {update_error}", exc_info=True)
            return False

    def delete_document(self, message: dict):
        knowledge_id = message.get('knowledge_id')
        doc_id = message.get('id')
        logger.info(f"Deleting document - Doc ID: {doc_id}, Knowledge ID: {knowledge_id}")
        try:
            self.qdrant.delete_document(collection_name=knowledge_id, doc_id=doc_id)
            logger.info(f"Successfully deleted document {doc_id} from vector store")
            return True
        except Exception as e:
            logger.error(f"Error deleting document {doc_id}: {e}", exc_info=True)
            return False

if __name__ == "__main__":
    rag = ChunkingRAG()
    # rag.upload_document(s3_key="s3://insightscanx/knowledge-data/rag/c534cc03-fd95-4f10-bad8-b8d3d0123683", 
    #     knowledge_name="7013e43a-a08e-4936-a884-23291ab2671e", file_name="test.pdf")
    print("Deleting document...")
    message = {
        "knowledge_id": "bdcaf41d-06f5-4a1b-80da-7c593592af44",
        "id": "dfc5b8c9-cccf-4937-a65f-aaef3caf904d"
    }
    rag.delete_document(message=message)
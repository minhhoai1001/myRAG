import os
import json
import logging
from confluent_kafka import Consumer

from src.rag import ChunkingRAG

# Setup logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('rag_worker')

def main():
    # Get Kafka broker URL from environment
    KAFKA_BROKER_URL = os.getenv("KAFKA_BROKER_URL", "kafka:9092")
    KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "rag.public.document")
    kafka_conf = {
        'bootstrap.servers': KAFKA_BROKER_URL,
        'group.id': 'rag_public_document_worker',
        'auto.offset.reset': 'earliest'
    }

    consumer = Consumer(kafka_conf)
    consumer.subscribe([KAFKA_TOPIC])

    rag = ChunkingRAG()

    try:
        logger.info(f"Subscribed to topic '{KAFKA_TOPIC}' on broker: {KAFKA_BROKER_URL}")
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                logger.error(f"Consumer error: {msg.error()}")
                continue
            
            # Check if message has value
            msg_value = msg.value()
            if msg_value is None:
                logger.warning("Received message with None value, skipping...")
                continue
            
            try:
                data = json.loads(msg_value.decode('utf-8'))
                payload = data.get('payload') 
                op = payload.get('op')
                if op == 'c':
                    message = payload.get('after')
                    doc_id = message.get('id') if message else 'unknown'
                    logger.info(f"Inserted row - Document ID: {doc_id}, Status: {message.get('status') if message else 'unknown'}")
                    # Don't process on insert - wait for status to change to "ingesting"
                    # File may not be uploaded to S3 yet
                elif op == 'd':
                    message = payload.get('before')
                    doc_id = message.get('id') if message else 'unknown'
                    logger.info(f"Deleted row - Document ID: {doc_id}")
                    rag.delete_document(message=message)
                elif op == 'u':
                    before = payload.get('before')
                    after = payload.get('after')
                    doc_id = after.get('id') if after else 'unknown'
                    before_status = before.get('status') if before else None
                    after_status = after.get('status') if after else None
                    
                    logger.debug(f"Updated row - Document ID: {doc_id}, Status: {before_status} -> {after_status}")
                    
                    # Only process when status changes to "ingesting"
                    # This ensures file has been uploaded to S3
                    if after_status == 'ingesting' and before_status != 'ingesting':
                        logger.info(f"Status changed to 'ingesting' for document {doc_id}, starting ingestion...")
                        try:
                            success = rag.upload_document(message=after)
                            if success:
                                logger.info(f"Successfully ingested document {doc_id}")
                            else:
                                logger.error(f"Failed to ingest document {doc_id}")
                        except Exception as e:
                            logger.error(f"Error ingesting document {doc_id}: {e}", exc_info=True)
                else:
                    logger.warning(f"Unknown operation: {op}")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to decode message: {e}")
            except Exception as e:
                logger.error(f"Failed to process message: {e}", exc_info=True)
    except KeyboardInterrupt:
        logger.info("Exiting on user interrupt.")
    finally:
        consumer.close()

if __name__ == "__main__":
    main()

import os
import json
from confluent_kafka import Consumer

def main():
    # Get Kafka broker URL from environment
    KAFKA_BROKER_URL = os.getenv("KAFKA_BROKER_URL", "kafka:9092")

    kafka_conf = {
        'bootstrap.servers': KAFKA_BROKER_URL,
        'group.id': 'rag_public_document_worker',
        'auto.offset.reset': 'earliest'
    }
    topic = "rag.public.document"

    consumer = Consumer(kafka_conf)
    consumer.subscribe([topic])

    try:
        print("Subscribed to topic 'rag.public.document' on broker:", KAFKA_BROKER_URL)
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                print(f"Consumer error: {msg.error()}")
                continue
            try:
                data = json.loads(msg.value().decode('utf-8'))
                payload = data.get('payload') 
                op = payload.get('op')
                if op == 'c':
                    print("Inserted row:", payload.get('after'))
                elif op == 'u':
                    print("Updated row:", payload.get('after'))
                elif op == 'd':
                    print("Deleted row:", payload.get('before'))
                else:
                    print("Unknown operation:", op)
            except Exception as e:
                print(f"Failed to process message: {e}")
    except KeyboardInterrupt:
        print("Exiting on user interrupt.")
    finally:
        consumer.close()

if __name__ == "__main__":
    main()

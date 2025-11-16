
## Setting Postgres
Connect db
```
podman exec -it rag-postgres bash
psql -U rag_user -d myrag
```
### Create publication for table need to track:
```
CREATE PUBLICATION debezium_pub FOR TABLE document;
ALTER TABLE document REPLICA IDENTITY FULL;
```

## Setting Debezium to track PostgreSQL
```
curl -X POST "http://localhost:8083/connectors" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "postgres-connector",
    "config": {
      "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
      "database.hostname": "postgres",
      "database.port": "5432",
      "database.user": "rag_user",
      "database.password": "rag.1234",
      "database.dbname": "myrag",
      "database.server.name": "postgres_server",
      "table.include.list": "public.document",
      "plugin.name": "pgoutput",
      "slot.name": "debezium_slot",
      "publication.name": "debezium_pub",
      "database.history.kafka.bootstrap.servers": "kafka:9092",
      "database.history.kafka.topic": "schema-changes",
      "topic.prefix": "rag"
    }
  }'
```

## Start RAG system
```
cd docker
docker-compose -f .\docker-compose.db.yml -f .\docker-compose.yml -p rag up -d
```
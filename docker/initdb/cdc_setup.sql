-- Configure PostgreSQL for Change Data Capture (CDC)
-- Allows PostgreSQL to record changes as a logical stream instead of a physical one
ALTER SYSTEM SET wal_level = logical;

-- Reloads the configuration without restarting the database
SELECT pg_reload_conf();

-- Set the replica identity for the document table to full
ALTER TABLE public.document REPLICA IDENTITY FULL;
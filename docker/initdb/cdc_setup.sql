-- Configure PostgreSQL for Change Data Capture (CDC)
-- Allows PostgreSQL to record changes as a logical stream instead of a physical one
ALTER SYSTEM SET wal_level = logical;

-- Reloads the configuration without restarting the database
SELECT pg_reload_conf();


#!/bin/bash
set -e

# Create database
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE elegant_agency;
    GRANT ALL PRIVILEGES ON DATABASE elegant_agency TO $POSTGRES_USER;
EOSQL

echo "Database 'elegant_agency' created successfully"

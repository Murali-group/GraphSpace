<<<<<<< HEAD
#!/usr/bin/env bash
=======
#!bin/sh
>>>>>>> actions-pipeline
echo "enabling pg_trgm & btree_gin on database $POSTGRES_DB"
psql -U $POSTGRES_USER --dbname="$POSTGRES_DB" <<-'EOSQL'
create extension if not exists pg_trgm;
create extension if not exists btree_gin;
EOSQL
echo "finished with exit code $?"
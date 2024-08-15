#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username postgres <<-EOSQL

  revoke all on database postgres from public;

  create user $DB_USER_SIRIUS with
    login
	  password '$DB_PASS_SIRIUS';

  create database $DB_NAME with
    encoding = 'utf8'
    lc_collate = 'en_US.utf8'
    lc_ctype = 'en_US.utf8'
    connection limit = -1;

  \connect $DB_NAME;

  create schema "$DB_SCHEMA_NAME_SIRIUS" authorization "$DB_USER_SIRIUS";

  grant all on schema "$DB_SCHEMA_NAME_SIRIUS" to "$DB_USER_SIRIUS";

  alter user $DB_USER_SIRIUS set search_path = 'public';

  create extension pg_stat_statements;

EOSQL

{
    echo "host all         pts       0.0.0.0/0      trust"
} >> "$PGDATA/pg_hba.conf"

#!/bin/bash
# wait-for-db.sh - Wait for PostgreSQL to be ready

set -e

host="$1"
port="$2"

echo "Waiting for PostgreSQL at $host:$port..."

until pg_isready -h "$host" -p "$port"; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done

echo "PostgreSQL is up and ready!"
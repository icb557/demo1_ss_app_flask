#!/bin/bash
# wait-for-db.sh (versión sin netcat)

set -e

host="$1"
port="$2"
shift 2
cmd="$@"

until (echo > /dev/tcp/$host/$port) >/dev/null 2>&1; do
  echo "Waiting for $host:$port..."
  sleep 2
done

exec $cmd
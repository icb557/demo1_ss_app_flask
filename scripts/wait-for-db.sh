#!/bin/sh
# Simple wait-for-db script

host="$1"
shift
cmd="$@"

echo "Waiting for $host:5432..."

for i in $(seq 30); do
    if nc -z "$host" 5432 > /dev/null 2>&1; then
        echo "$host is ready!"
        break
    fi
    
    if [ $i -eq 30 ]; then
        echo "Timeout waiting for $host"
        exit 1
    fi
    
    sleep 2
done

# Execute command if provided
if [ -n "$cmd" ]; then
    exec $cmd
fi
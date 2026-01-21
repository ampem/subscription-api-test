#!/bin/bash
set -e

if [ -z "$1" ]; then
    echo "Error: Migration version is required"
    echo "Usage: make migrate-to version=abc123"
    echo ""
    echo "Available migrations:"
    docker compose exec api alembic history
    exit 1
fi

docker compose exec api alembic upgrade "$1"

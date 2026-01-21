#!/bin/bash
set -e

if [ -z "$1" ]; then
    echo "Error: Migration name is required"
    echo "Usage: make migration name='description of migration'"
    exit 1
fi

docker compose exec api alembic revision --autogenerate -m "$1"

#!/bin/bash
set -e

docker compose exec api alembic upgrade head

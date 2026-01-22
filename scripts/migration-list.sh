#!/bin/bash
set -e

# Get current revision
CURRENT=$(docker compose exec -T api alembic current 2>/dev/null | grep -oE '^[a-f0-9]+' || echo "")

# Get history and mark current
docker compose exec -T api alembic history | while read -r line; do
    # Extract revision from the line (format: "rev_id -> next_rev_id (head), description" or "rev_id -> , description")
    REV=$(echo "$line" | grep -oE '^[a-f0-9]+' || echo "")
    if [ -n "$REV" ] && [ "$REV" = "$CURRENT" ]; then
        echo "* $line"
    else
        echo "  $line"
    fi
done

#!/bin/bash
set -e

ENV="${TF_VAR_ENVIRONMENT:-staging}"
TFVARS_FILE="terraform/${ENV}/terraform.tfvars.json"

if [ ! -f "$TFVARS_FILE" ]; then
    echo "Error: $TFVARS_FILE not found"
    exit 1
fi

MIGRATION_LEVEL=$(jq -r '.migration_level' "$TFVARS_FILE")

if [ -z "$MIGRATION_LEVEL" ] || [ "$MIGRATION_LEVEL" = "null" ]; then
    echo "Error: migration_level not found in $TFVARS_FILE"
    exit 1
fi

echo "Running migration to level: $MIGRATION_LEVEL"

aws lambda invoke \
    --function-name "shade-subscription-api-${ENV}-migrate" \
    --payload "{\"revision\": \"${MIGRATION_LEVEL}\"}" \
    --cli-binary-format raw-in-base64-out \
    response.json

echo "Migration response:"
cat response.json

# Check if migration was successful
if grep -q '"statusCode": 500' response.json; then
    echo "Migration failed!"
    rm -f response.json
    exit 1
fi

rm -f response.json
echo "Migration completed successfully"

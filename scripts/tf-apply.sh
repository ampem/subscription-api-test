#!/bin/bash
set -e

ENV="${TF_VAR_ENVIRONMENT:-staging}"

if [ -n "$CI" ]; then
    # Running in CI (GitHub Actions)
    terraform -chdir="terraform/${ENV}" apply -auto-approve -var-file=terraform.tfvars.json
else
    # Running locally with docker compose
    docker compose exec -w /terraform/${ENV} terraform terraform apply -var-file=terraform.tfvars.json
fi

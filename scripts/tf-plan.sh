#!/bin/bash
set -e

ENV="${TF_VAR_environment:-staging}"

if [ -n "$CI" ]; then
    # Running in CI (GitHub Actions)
    terraform -chdir="terraform/${ENV}" plan -var-file=terraform.tfvars.json
else
    # Running locally with docker compose
    docker compose exec -w /terraform/${ENV} terraform terraform plan -var-file=terraform.tfvars.json
fi

#!/bin/bash
set -e

docker compose exec -w /terraform/staging terraform terraform plan

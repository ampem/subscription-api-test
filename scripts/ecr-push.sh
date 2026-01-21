#!/bin/bash
set -e

ENVIRONMENT="${1:-staging}"
REGION="${2:-us-east-1}"
TAG="${3:-latest}"
IMAGE_NAME="shade-subscription-api-${ENVIRONMENT}"

echo "Getting AWS account ID..."
ACCOUNT_ID=$(docker compose exec -T aws aws sts get-caller-identity --query Account --output text)
echo "Account ID: ${ACCOUNT_ID}"

ECR_URL="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com"
FULL_IMAGE_URL="${ECR_URL}/${IMAGE_NAME}:${TAG}"

echo "Logging in to ECR..."
docker compose exec -T aws aws ecr get-login-password --region "${REGION}" | \
    docker login --username AWS --password-stdin "${ECR_URL}"

echo "Building ${IMAGE_NAME}:${TAG}..."
docker build -f api/Dockerfile.lambda -t "${IMAGE_NAME}:${TAG}" ./api

echo "Tagging image for ECR..."
docker tag "${IMAGE_NAME}:${TAG}" "${FULL_IMAGE_URL}"

echo "Pushing to ECR..."
docker push "${FULL_IMAGE_URL}"

echo ""
echo "Successfully pushed ${FULL_IMAGE_URL}"

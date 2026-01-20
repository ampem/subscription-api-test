# Shade Subscription API

The backend for the remote controlled shade control service.
A FastAPI application deployed to AWS Lambda via Terraform.

## Technologies

- **Python 3.14** - Runtime
- **FastAPI** - Web framework
- **Mangum** - AWS Lambda adapter for ASGI apps
- **Uvicorn** - ASGI server (local development)
- **Terraform** - Infrastructure as code
- **AWS Lambda** - Serverless compute
- **AWS S3** - Terraform state storage
- **Docker Compose** - Local development environment

## Project Structure

```
.
├── api/                 # FastAPI application
├── terraform/           # Infrastructure as code
├── frontend/            # Frontend application (if implemented)
├── docker-compose.yml   # Local development containers
└── .env.example         # Environment variables template
```

## Environments

| Environment | API Host                        | Terraform State Bucket              |
|-------------|---------------------------------|-------------------------------------|
| Staging     | api.staging.shade.accretors.org | shade-accretors-tfstate-staging     |
| Production  | api.shade.accretors.org         | shade-accretors-tfstate-production  |

## Local Development

1. Copy the environment template:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your AWS credentials and user IDs.

3. Start the services:
   ```bash
   docker compose up -d
   ```

4. Access the API at http://localhost:8000 (docs at http://localhost:8000/docs).

## Creating Terraform State Buckets

Before deploying infrastructure, create S3 buckets to store Terraform state.

### Staging

```bash
docker compose exec aws aws s3api create-bucket \
  --bucket shade-accretors-tfstate-staging \
  --region us-east-1

docker compose exec aws aws s3api put-bucket-versioning \
  --bucket shade-accretors-tfstate-staging \
  --versioning-configuration Status=Enabled

docker compose exec aws aws s3api put-bucket-encryption \
  --bucket shade-accretors-tfstate-staging \
  --server-side-encryption-configuration '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'

docker compose exec aws aws s3api put-public-access-block \
  --bucket shade-accretors-tfstate-staging \
  --public-access-block-configuration BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
```

### Production

```bash
docker compose exec aws aws s3api create-bucket \
  --bucket shade-accretors-tfstate-production \
  --region us-east-1

docker compose exec aws aws s3api put-bucket-versioning \
  --bucket shade-accretors-tfstate-production \
  --versioning-configuration Status=Enabled

docker compose exec aws aws s3api put-bucket-encryption \
  --bucket shade-accretors-tfstate-production \
  --server-side-encryption-configuration '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'

docker compose exec aws aws s3api put-public-access-block \
  --bucket shade-accretors-tfstate-production \
  --public-access-block-configuration BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
```

> **Note:** For regions other than `us-east-1`, add `--create-bucket-configuration LocationConstraint=<region>` to the create-bucket command.

## Running Terraform

```bash
docker compose exec terraform terraform init
docker compose exec terraform terraform plan
docker compose exec terraform terraform apply
```

## Running AWS CLI Commands

```bash
docker compose exec aws aws sts get-caller-identity
docker compose exec aws aws s3 ls
```

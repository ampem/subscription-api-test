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

## Database Migrations

Run Alembic migrations to set up the database schema:

```bash
docker compose exec api alembic upgrade head
```

To create a new migration after modifying models:

```bash
docker compose exec api alembic revision --autogenerate -m "description of changes"
```

## Test Data

A script is provided to generate seed data for development and testing.

### Generate seed data

```bash
# Generate SQL file with 50 users (default)
docker compose exec api python scripts/generate_seed_data.py

# Generate with custom number of users
docker compose exec api python scripts/generate_seed_data.py --users 100

# Specify output file
docker compose exec api python scripts/generate_seed_data.py --users 100 --output my_seed_data.sql
```

### Apply seed data to database

```bash
docker compose exec db mariadb -u shade -pshade shade < api/seed_data.sql
```

### What the seed data includes

| Category | Description |
|----------|-------------|
| **Plans** | |
| Current year | Free, Basic, Pro plans (monthly & yearly) active for all of current year |
| Next year | Same tiers with 10% price increase, active next year |
| Simulation | Plans marked with `simulation=true` for testing |
| **Users** | |
| No subscription | ~15% of users have no subscriptions |
| Simulation mode | ~10% of users in simulation mode with simulation plans |
| Active subscriptions | ~40% of users with active free/basic/pro subscriptions |
| Lapsed subscriptions | ~20% of users with expired or cancelled subscriptions |
| Future subscriptions | ~15% of users with subscriptions starting in the future |

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

## ECR Authentication

To push Docker images to ECR, authenticate Docker with your registry.

### Get your AWS account ID

```bash
docker compose exec aws aws sts get-caller-identity --query Account --output text
```

### Login to ECR

```bash
docker compose exec aws aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
```

Replace `<account-id>` with your AWS account ID from the previous command.

### Build and push an image

```bash
# Build the Lambda image
docker build -f api/Dockerfile.lambda -t shade-subscription-api-staging:latest ./api

# Tag for ECR
docker tag shade-subscription-api-staging:latest \
  <account-id>.dkr.ecr.us-east-1.amazonaws.com/shade-subscription-api-staging:latest

# Push to ECR
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/shade-subscription-api-staging:latest
```

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

## Architecture Diagram

This diagram represents the high-level architecture of the subscription API.

<img width="1318" height="1046" alt="image" src="https://github.com/user-attachments/assets/b2c9ea59-bee4-4bd1-bab4-562596884bf2" />


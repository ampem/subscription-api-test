variable "AWS_REGION" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "ENVIRONMENT" {
  description = "Deployment environment (staging, production)"
  type        = string
}

variable "IMAGE_TAG" {
  description = "Docker image tag for the Lambda function"
  type        = string
  default     = "latest"
}

variable "MIGRATION_IMAGE_TAG" {
  description = "Docker image tag for the migration Lambda function"
  type        = string
  default     = "latest"
}

variable "MIGRATION_LEVEL" {
  description = "Alembic migration revision to migrate to"
  type        = string
}

variable "ROUTE53_ZONE_ID" {
  description = "Route53 hosted zone ID"
  type        = string
}

variable "POSTGRES_DB_NAME" {
  description = "The name of the PostgreSQL database"
  type        = string
  sensitive   = true
}

variable "POSTGRES_DB_USERNAME" {
  description = "The username for the PostgreSQL database"
  type        = string
  sensitive   = true
}

variable "POSTGRES_DB_PASSWORD" {
  description = "The password for the PostgreSQL database"
  type        = string
  sensitive   = true
}

variable "VPC_ID" {
  description = "The ID of the VPC to use for resources"
  type        = string
}

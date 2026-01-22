variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Deployment environment (staging, production)"
  type        = string
}

variable "image_tag" {
  description = "Docker image tag for the Lambda function"
  type        = string
  default     = "latest"
}

variable "migration_image_tag" {
  description = "Docker image tag for the migration Lambda function"
  type        = string
  default     = "latest"
}

variable "migration_level" {
  description = "Alembic migration revision to migrate to"
  type        = string
}

variable "route53_zone_id" {
  description = "Route53 hosted zone ID"
  type        = string
}

variable "mariadb_db_name" {
  description = "The name of the MariaDB database"
  type        = string
  sensitive   = true
}

variable "mariadb_db_username" {
  description = "The username for the MariaDB database"
  type        = string
  sensitive   = true
}

variable "mariadb_db_password" {
  description = "The password for the MariaDB database"
  type        = string
  sensitive   = true
}

variable "vpc_id" {
  description = "The ID of the VPC to use for resources"
  type        = string
}

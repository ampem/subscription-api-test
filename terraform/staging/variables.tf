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

variable "route53_zone_id" {
  description = "Route53 hosted zone ID"
  type        = string
}

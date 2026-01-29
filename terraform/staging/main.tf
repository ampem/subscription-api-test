terraform {
  required_version = ">= 1.14.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket = "shade-accretors-tfstate-staging"
    key    = "terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = var.AWS_REGION
}

locals {
  project_name = "shade-subscription-api"
  api_domain   = var.ENVIRONMENT == "production" ? "api.shade.accretors.org" : "api.${var.ENVIRONMENT}.shade.accretors.org"
}

# IAM Role for Lambda
resource "aws_iam_role" "lambda_role" {
  name = "${local.project_name}-${var.ENVIRONMENT}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# ECR Repository
resource "aws_ecr_repository" "api" {
  name                 = "${local.project_name}-${var.ENVIRONMENT}"
  image_tag_mutability = "MUTABLE"
  force_delete         = false

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_lifecycle_policy" "api" {
  repository = aws_ecr_repository.api.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 10 images"
        selection = {
          tagStatus   = "any"
          countType   = "imageCountMoreThan"
          countNumber = 10
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}

# VPC Configuration (assuming a VPC exists; use your VPC ID)
data "aws_subnets" "private" {
  filter {
    name   = "vpc-id"
    values = [var.VPC_ID]
  }
}

resource "aws_security_group" "lambda_sg" {
  name        = "lambda_sg"
  description = "Security group for Lambda"
  vpc_id      = var.VPC_ID

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "rds_sg" {
  name        = "rds_sg"
  description = "Security group for RDS"
  vpc_id      = var.VPC_ID  # Using variable as originally intended

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.lambda_sg.id]  # Only allow from Lambda SG
  }
  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["15.235.193.126/32"]  # Allow access from bastion host
  }
  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["217.46.64.84/32"]  # Allow access from laptop
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Lambda Function
resource "aws_lambda_function" "api" {
  function_name = "${local.project_name}-${var.ENVIRONMENT}"
  role          = aws_iam_role.lambda_role.arn
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.api.repository_url}:${var.IMAGE_TAG}"
  timeout       = 30
  memory_size   = 256

  environment {
    variables = {
      ENVIRONMENT  = var.ENVIRONMENT
      DATABASE_URL = "postgresql+psycopg2://${var.POSTGRES_DB_USERNAME}:${var.POSTGRES_DB_PASSWORD}@${aws_db_instance.postgres.endpoint}/${var.POSTGRES_DB_NAME}"
    }
  }

  vpc_config {
    subnet_ids         = data.aws_subnets.private.ids
    security_group_ids = [aws_security_group.lambda_sg.id]
  }
}

# Lambda Function URL (alternative to API Gateway)
resource "aws_lambda_function_url" "api" {
  function_name      = aws_lambda_function.api.function_name
  authorization_type = "NONE"
}

# API Gateway HTTP API
resource "aws_apigatewayv2_api" "api" {
  name          = "${local.project_name}-${var.ENVIRONMENT}"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_stage" "api" {
  api_id      = aws_apigatewayv2_api.api.id
  name        = "$default"
  auto_deploy = true
}

resource "aws_apigatewayv2_integration" "api" {
  api_id                 = aws_apigatewayv2_api.api.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.api.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "api" {
  api_id    = aws_apigatewayv2_api.api.id
  route_key = "$default"
  target    = "integrations/${aws_apigatewayv2_integration.api.id}"
}

resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.api.execution_arn}/*/*"
}

# Route53 Hosted Zone (existing)
data "aws_route53_zone" "main" {
  zone_id = var.ROUTE53_ZONE_ID
}

# ACM Certificate for custom domain
resource "aws_acm_certificate" "api" {
  domain_name       = local.api_domain
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_route53_record" "cert_validation" {
  for_each = {
    for dvo in aws_acm_certificate.api.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  zone_id = data.aws_route53_zone.main.zone_id
  name    = each.value.name
  type    = each.value.type
  records = [each.value.record]
  ttl     = 60
}

resource "aws_acm_certificate_validation" "api" {
  certificate_arn         = aws_acm_certificate.api.arn
  validation_record_fqdns = [for record in aws_route53_record.cert_validation : record.fqdn]
}

# API Gateway Custom Domain
resource "aws_apigatewayv2_domain_name" "api" {
  domain_name = local.api_domain

  domain_name_configuration {
    certificate_arn = aws_acm_certificate_validation.api.certificate_arn
    endpoint_type   = "REGIONAL"
    security_policy = "TLS_1_2"
  }
}

resource "aws_apigatewayv2_api_mapping" "api" {
  api_id      = aws_apigatewayv2_api.api.id
  domain_name = aws_apigatewayv2_domain_name.api.id
  stage       = aws_apigatewayv2_stage.api.id
}

# DNS Record for API
resource "aws_route53_record" "api" {
  zone_id = data.aws_route53_zone.main.zone_id
  name    = local.api_domain
  type    = "A"

  alias {
    name                   = aws_apigatewayv2_domain_name.api.domain_name_configuration[0].target_domain_name
    zone_id                = aws_apigatewayv2_domain_name.api.domain_name_configuration[0].hosted_zone_id
    evaluate_target_health = false
  }
}

resource "aws_db_instance" "postgres" {
  engine                 = "postgres"
  engine_version         = "18.1"
  instance_class         = "db.t3.micro"
  allocated_storage      = 5
  db_name                = var.POSTGRES_DB_NAME
  username               = var.POSTGRES_DB_USERNAME
  password               = var.POSTGRES_DB_PASSWORD
  skip_final_snapshot    = true
  publicly_accessible    = true
  vpc_security_group_ids = [aws_security_group.rds_sg.id]
}

# IAM Policy for RDS Access
resource "aws_iam_role_policy" "lambda_rds_access" {
  name = "lambda_rds_access"
  role = aws_iam_role.lambda_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "rds-db:connect"
        ]
        Resource = aws_db_instance.postgres.arn
      }
    ]
  })
}

# IAM Policy for VPC access (required for Lambda in VPC)
resource "aws_iam_role_policy_attachment" "lambda_vpc_access" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

# Migration Lambda Function (uses same image with different handler)
resource "aws_lambda_function" "migrate" {
  function_name = "${local.project_name}-${var.ENVIRONMENT}-migrate"
  role          = aws_iam_role.lambda_role.arn
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.api.repository_url}:${var.MIGRATION_IMAGE_TAG}"
  timeout       = 300
  memory_size   = 256

  image_config {
    command = ["migrate.handler"]
  }

  environment {
    variables = {
      ENVIRONMENT  = var.ENVIRONMENT
      DATABASE_URL = "postgresql+psycopg2://${var.POSTGRES_DB_USERNAME}:${var.POSTGRES_DB_PASSWORD}@${aws_db_instance.postgres.endpoint}/${var.POSTGRES_DB_NAME}"
    }
  }

  vpc_config {
    subnet_ids         = data.aws_subnets.private.ids
    security_group_ids = [aws_security_group.lambda_sg.id]
  }
}

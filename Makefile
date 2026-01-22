.PHONY: tf-plan tf-apply migration migrate migrate-to migrate-list test lint-commit ecr-push help

help:
	@echo "Available targets:"
	@echo "  tf-plan          - Run terraform plan for staging"
	@echo "  tf-apply         - Run terraform apply for staging"
	@echo "  migration        - Create a new alembic migration (usage: make migration name='description')"
	@echo "  migrate          - Run all pending migrations (alembic upgrade head)"
	@echo "  migrate-to       - Migrate to a specific version (usage: make migrate-to version=abc123)"
	@echo "  migrate-list     - List all migrations (* marks current)"
	@echo "  test             - Run tests"
	@echo "  lint-commit      - Lint the most recent commit message"
	@echo "  ecr-push         - Build and push API image to ECR (usage: make ecr-push env=staging region=us-east-1 tag=v1.0.0)"

tf-plan:
	@./scripts/tf-plan.sh

tf-apply:
	@./scripts/tf-apply.sh

migration:
	@./scripts/migration-create.sh "$(name)"

migrate:
	@./scripts/migration-head.sh

migrate-to:
	@./scripts/migration-to.sh "$(version)"

migrate-list:
	@./scripts/migration-list.sh

test:
	@./scripts/test.sh

lint-commit:
	@./scripts/lint-commit.sh

ecr-push:
	@./scripts/ecr-push.sh "$(env)" "$(region)" "$(tag)"

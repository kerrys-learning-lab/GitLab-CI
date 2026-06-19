terraform {
  required_version = ">= 1.5"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Region comes from AWS_REGION / AWS_DEFAULT_REGION env var, the
# provider's shared config, or the `aws_region` variable below.
provider "aws" {
  region = var.aws_region
}

# --- "Hello, world" connectivity checks ------------------------------------
# These are *data sources*: they only read from AWS. No resources are
# created, so the plan/apply is free and leaves nothing to destroy.

# Verifies credentials are valid by resolving the caller's identity (STS).
data "aws_caller_identity" "current" {}

# Confirms the configured region resolves.
data "aws_region" "current" {}

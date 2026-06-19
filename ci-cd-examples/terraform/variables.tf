variable "aws_region" {
  description = "AWS region to connect to. Falls back to the AWS_REGION env var if unset."
  type        = string
  default     = "us-east-1"
}

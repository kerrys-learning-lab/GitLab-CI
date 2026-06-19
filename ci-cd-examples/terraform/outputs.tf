output "greeting" {
  description = "Hello, world — proof we reached AWS."
  value = format(
    "Hello, world! Connected to AWS account %s as %s in region %s.",
    data.aws_caller_identity.current.account_id,
    data.aws_caller_identity.current.arn,
    data.aws_region.current.name,
  )
}

output "account_id" {
  description = "The AWS account ID the credentials belong to."
  value       = data.aws_caller_identity.current.account_id
}

# hello-terraform

A minimal Terraform configuration for exercising a CI/CD pipeline. It connects
to AWS and proves the credentials work **without creating any billable
resources** — it uses only data sources (`aws_caller_identity`, `aws_region`),
which read from AWS but provision nothing.

## What it validates

- Terraform init / provider download
- `fmt` and `validate` (static checks, no cloud access)
- `plan` / `apply` connecting to AWS with real credentials (STS `GetCallerIdentity`)

## Local usage

```bash
export AWS_REGION=us-east-1          # or set var.aws_region
terraform init
terraform fmt -check
terraform validate
terraform plan
terraform apply -auto-approve        # prints the greeting; creates nothing
```

Because nothing is created, `terraform destroy` is a no-op.

## Pipeline usage

A typical pipeline stage list:

| Stage      | Command                          | Needs AWS creds? |
| ---------- | -------------------------------- | ---------------- |
| `fmt`      | `terraform fmt -check -recursive`| no               |
| `validate` | `terraform init -backend=false && terraform validate` | no |
| `plan`     | `terraform plan`                 | yes              |
| `apply`    | `terraform apply -auto-approve`  | yes              |

The `fmt` and `validate` stages run without credentials, so they're a cheap
fast-fail gate. The `plan`/`apply` stages exercise the actual cloud connection.

## Credentials

The AWS provider picks up credentials from the standard chain — environment
variables (`AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` / `AWS_SESSION_TOKEN`),
an OIDC-assumed role in CI, or an instance/IRSA role. Nothing is hardcoded.

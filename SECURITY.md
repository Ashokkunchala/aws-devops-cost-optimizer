# Security Policy

## Supported version

The latest commit on `main` is the actively developed version.

## Reporting a vulnerability

Do not publish credentials, account IDs, customer data, or exploitable details in public issues. Use GitHub's private vulnerability reporting feature if available; otherwise contact the maintainer through a verified private channel.

## Security limits

The starter collector uses read-only EC2 Describe APIs. This is not a formal security audit. Review IAM permissions, dependencies, and output before use. Never commit AWS keys, Terraform state, account-specific reports, or customer data.

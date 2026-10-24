# Security Policy

## Supported versions

The latest commit on `main` is the version actively developed.

## Reporting a vulnerability

Do not publish credentials, account IDs, customer data, or exploitable details in public issues. Use GitHub's private vulnerability reporting feature for this repository if available; otherwise contact the maintainer privately through a verified channel.

## Security limits

The starter collector uses read-only EC2 Describe APIs. This is not a formal security audit and does not guarantee AWS-account safety. Review IAM permissions, dependencies, and output before use. Never commit AWS keys, Terraform state, account-specific reports, or customer data.

# Optional AWS Budget Alert

This example creates a monthly AWS cost budget with email notifications. It is not applied by CI and is not required to use the scanner.

## Before use

- Review current AWS Budgets pricing, eligibility, and account limits.
- Replace the placeholder email in `terraform.tfvars`.
- Review `terraform plan` and validate currency/account scope.
- The recipient may need to confirm notification subscription.
- This example creates no compute or networking resources.

```bash
terraform init
terraform validate
terraform plan -var='notification_email=you@example.com'
# Only after reviewing the plan:
terraform apply -var='notification_email=you@example.com'
```

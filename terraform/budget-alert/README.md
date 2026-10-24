# Optional AWS Budget Alert

Creates an AWS monthly cost budget with email notifications. It is not applied by CI and is not required to use the scanner.

Before use, review current AWS Budgets pricing, eligibility, and account limits. Set a real recipient email, inspect the Terraform plan, and confirm currency/account scope. The recipient may need to confirm the notification subscription. This example creates no compute or networking.

```bash
terraform init
terraform validate
terraform plan -var='notification_email=you@example.com'
# Only after reviewing the plan:
terraform apply -var='notification_email=you@example.com'
```

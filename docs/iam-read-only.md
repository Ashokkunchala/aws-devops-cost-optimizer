# Read-only IAM setup

Use a dedicated audit role or IAM Identity Center permission set. Do not use root credentials or put long-lived access keys in source code.

Required EC2 actions for this inventory starter:

- `ec2:DescribeInstances`
- `ec2:DescribeVolumes`

Example statement for a learning account (review before production):

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "ReadOnlyEc2Inventory",
    "Effect": "Allow",
    "Action": ["ec2:DescribeInstances", "ec2:DescribeVolumes"],
    "Resource": "*"
  }]
}
```

Some Describe actions do not support resource-level restrictions. Validate permissions against current AWS documentation and IAM Access Analyzer.

Configure a profile named `cost-audit` with approved SSO or role assumption:

```bash
aws sts get-caller-identity --profile cost-audit
python -m cost_optimizer --aws --profile cost-audit --region ap-south-1 --output reports/aws-report.json
```

The tool does not call StopInstances, ModifyInstanceAttribute, DeleteVolume, DetachVolume, or any mutation API. Do not add write permissions to this role.

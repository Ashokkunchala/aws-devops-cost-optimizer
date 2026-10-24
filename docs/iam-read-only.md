# Read-only IAM setup

Use a dedicated audit role or IAM Identity Center permission set. Do not use root credentials or long-lived access keys in source code.

For the inventory-only starter, the required EC2 operations are:

- `ec2:DescribeInstances`
- `ec2:DescribeVolumes`

Example policy statement for a learning account (review before production use):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ReadOnlyEc2Inventory",
      "Effect": "Allow",
      "Action": ["ec2:DescribeInstances", "ec2:DescribeVolumes"],
      "Resource": "*"
    }
  ]
}
```

Some Describe APIs do not support resource-level restrictions. Validate the policy with AWS documentation and IAM Access Analyzer.

If using a profile named `cost-audit`, configure it locally through an approved SSO or role assumption workflow:

```bash
aws sts get-caller-identity --profile cost-audit
python -m cost_optimizer --aws --profile cost-audit --region ap-south-1 --output reports/aws-report.json
```

The tool makes no StopInstances, ModifyInstanceAttribute, DeleteVolume, DetachVolume, or other mutation calls. Do not add write permissions to this role.

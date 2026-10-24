# Read-only IAM setup

Use a dedicated audit role or IAM Identity Center permission set. Do not use root credentials or put long-lived access keys in source code.

Required actions for inventory and CPU analysis:

- `ec2:DescribeInstances`
- `ec2:DescribeVolumes`
- `cloudwatch:GetMetricStatistics`

Example statement for a learning account (review before production):

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "ReadOnlyEc2InventoryAndCpuMetrics",
    "Effect": "Allow",
    "Action": [
      "ec2:DescribeInstances",
      "ec2:DescribeVolumes",
      "cloudwatch:GetMetricStatistics"
    ],
    "Resource": "*"
  }]
}
```

Some Describe and metric read APIs do not support resource-level restrictions. Validate permissions against current AWS documentation and IAM Access Analyzer.

Configure a profile named `cost-audit` with approved SSO or role assumption:

```bash
aws sts get-caller-identity --profile cost-audit
python -m cost_optimizer --aws --profile cost-audit --region ap-south-1 --lookback-days 14 --output reports/aws-report.json
```

The scanner requests hourly average and maximum CPU for each running instance over the selected lookback (1–90 days). Missing metrics are reported as unavailable, not treated as zero. API request volume grows with the number of running instances; use this only in an approved audit cadence.

The tool does not call StopInstances, ModifyInstanceAttribute, DeleteVolume, DetachVolume, or any mutation API. Do not add write permissions to this role.

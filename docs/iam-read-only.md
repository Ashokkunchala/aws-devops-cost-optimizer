# Read-only IAM setup

Use a dedicated audit role or IAM Identity Center permission set. Do not use root credentials or put long-lived access keys in source code.

Required actions for inventory and CPU analysis:
- ec2:DescribeInstances
- ec2:DescribeVolumes
- cloudwatch:GetMetricStatistics

Optional billing integration:
- ce:GetCostAndUsage

Example policy for a learning account (review before production):

    {
      "Version": "2012-10-17",
      "Statement": [{
        "Sid": "ReadOnlyCostOptimizer",
        "Effect": "Allow",
        "Action": [
          "ec2:DescribeInstances",
          "ec2:DescribeVolumes",
          "cloudwatch:GetMetricStatistics",
          "ce:GetCostAndUsage"
        ],
        "Resource": "*"
      }]
    }

Some read APIs do not support resource-level restrictions. Validate permissions with current AWS documentation and IAM Access Analyzer. If billing access should be separated from inventory, use a separate role/policy for Cost Explorer.

Configure an approved SSO or role-assumption profile, then verify identity:

    aws sts get-caller-identity --profile cost-audit

The CPU collector requests hourly averages/maxima over 1–90 days for each running instance. Cost Explorer uses monthly UnblendedCost groups by service; its End date is exclusive. The tool does not call StopInstances, ModifyInstanceAttribute, DeleteVolume, DetachVolume, or any mutation API.

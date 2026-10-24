# Container usage

The image packages the CLI and optional Boto3 dependency. It runs as a non-root user and does not include AWS credentials.

## Build

    docker build -t aws-devops-cost-optimizer:local .

## Local fixture scan

From the repository root, mount the source read-only and mount an output directory that is writable by the container user:

    mkdir -p reports
    docker run --rm \
      -v "$PWD/examples:/inputs:ro" \
      -v "$PWD/reports:/reports" \
      aws-devops-cost-optimizer:local \
      --input /inputs/sample_inventory.json \
      --output /reports/report.json \
      --html-output /reports/report.html

On Windows PowerShell, replace $PWD with ${PWD} in volume paths. Ensure the reports directory is writable by the container's UID (10001 on typical Linux Docker installations); do not solve permissions by running the scanner as root in production.

## Read-only AWS scan

Use an approved short-lived role or IAM Identity Center session. Mount only the needed AWS config/credential files read-only; never bake credentials into the image.

    docker run --rm \
      -e AWS_PROFILE=cost-audit \
      -v "$HOME/.aws:/home/app/.aws:ro" \
      -v "$PWD/reports:/reports" \
      aws-devops-cost-optimizer:local \
      --aws --profile cost-audit --region ap-south-1 \
      --output /reports/aws-report.json --html-output /reports/aws-report.html

Credential file paths differ by OS and setup. Validate the mounted path and use SSO/role credentials where possible. The required IAM actions are listed in docs/iam-read-only.md.

## Billing costs

Add the Cost Explorer flags shown in the root README. This makes read-only billing API calls and requires ce:GetCostAndUsage. No resources are deployed by the container.

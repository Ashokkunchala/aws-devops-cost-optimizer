variable "project_name" {
  description = "Prefix for the AWS Budget resource."
  type        = string
  default     = "aws-devops-cost-optimizer"
}

variable "aws_region" {
  description = "AWS region for provider configuration."
  type        = string
  default     = "ap-south-1"
}

variable "monthly_budget_amount" {
  description = "Monthly budget limit in the selected currency."
  type        = string
  default     = "10"

  validation {
    condition     = can(regex("^[0-9]+([.][0-9]{1,2})?$", var.monthly_budget_amount)) && tonumber(var.monthly_budget_amount) > 0
    error_message = "monthly_budget_amount must be a positive number with at most two decimal places."
  }
}

variable "currency" {
  description = "Currency accepted by AWS Budgets, for example USD."
  type        = string
  default     = "USD"
}

variable "notification_email" {
  description = "Email to receive budget notifications. Set a real recipient before planning."
  type        = string
  default     = "replace-me@example.com"

  validation {
    condition     = can(regex("^[^@ ]+@[^@ ]+[.][^@ ]+$", var.notification_email)) && var.notification_email != "replace-me@example.com"
    error_message = "Set notification_email to a real recipient address before running Terraform."
  }
}

variable "actual_threshold_percent" {
  description = "Actual spend threshold as a percentage of budget."
  type        = number
  default     = 80

  validation {
    condition     = var.actual_threshold_percent > 0 && var.actual_threshold_percent <= 1000
    error_message = "Threshold must be greater than zero and at most 1000."
  }
}

variable "forecasted_threshold_percent" {
  description = "Forecasted spend threshold as a percentage of budget."
  type        = number
  default     = 100

  validation {
    condition     = var.forecasted_threshold_percent > 0 && var.forecasted_threshold_percent <= 1000
    error_message = "Threshold must be greater than zero and at most 1000."
  }
}

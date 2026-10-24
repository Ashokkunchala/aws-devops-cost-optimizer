output "budget_name" {
  description = "Name of the monthly AWS cost budget."
  value       = aws_budgets_budget.monthly_cost.name
}

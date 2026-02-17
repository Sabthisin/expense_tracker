# accounts/services/budget_service.py
from accounts.models import Budget
from expenses.models import Expense
from django.db.models import Sum
from .alert_service import send_budget_alert

def update_budget_spent(user, category):
    # Calculate total spent
    total_spent = Expense.objects.filter(
        user=user,
        category=category
    ).aggregate(total=Sum('amount'))['total'] or 0

    try:
        budget = Budget.objects.get(user=user, category=category)
        budget.spent = total_spent
        budget.save()
        check_budget_alert(budget)
    except Budget.DoesNotExist:
        return None

    return budget

def check_budget_alert(budget):
    percent = budget.deviation_percentage()

    # Warning 80-99%
    if 80 <= percent < 100 and budget.last_alert != "warning":
        send_budget_alert(
            budget.user,
            budget.category.name,
            budget.limit_amount,
            budget.spent,
            "Warning (80% Budget Used)"
        )
        budget.last_alert = "warning"
        budget.save()

    # Critical 100%
    elif percent == 100 and budget.last_alert != "critical":
        send_budget_alert(
            budget.user,
            budget.category.name,
            budget.limit_amount,
            budget.spent,
            "Critical (Budget Reached)"
        )
        budget.last_alert = "critical"
        budget.save()

    # Exceeded >100%
    elif percent > 100 and budget.last_alert != "exceeded":
        send_budget_alert(
            budget.user,
            budget.category.name,
            budget.limit_amount,
            budget.spent,
            "Exceeded (Over Budget!)"
        )
        budget.last_alert = "exceeded"
        budget.save()

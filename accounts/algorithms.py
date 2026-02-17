from datetime import datetime
from django.db.models import Sum
from .models import Budget, Expense, Category

# -------------------------------
# Expense Categorization Algorithm
# -------------------------------
CATEGORY_KEYWORDS = {
    "Food": ["restaurant", "cafe", "dinner", "lunch", "breakfast", "food", "snack"],
    "Transport": ["bus", "taxi", "uber", "train", "fuel", "petrol", "transport"],
    "Shopping": ["mall", "clothes", "shoes", "shopping", "purchase", "online"],
    "Bills": ["electricity", "water", "internet", "rent", "bill", "subscription"],
    "Entertainment": ["movie", "cinema", "game", "netflix", "entertainment"],
    "Health": ["doctor", "medicine", "hospital", "health", "pharmacy"],
}

def categorize_expense(expense):
    description = (expense.description or "").lower()
    for category_name, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in description for keyword in keywords):
            category, _ = Category.objects.get_or_create(name=category_name)
            expense.category = category
            expense.save()
            return category_name
    # Default category
    category, _ = Category.objects.get_or_create(name="Others")
    expense.category = category
    expense.save()
    return "Others"

# -------------------------------
# Budget Deviation Detection Algorithm
# -------------------------------
def detect_budget_deviation(user):
    current_month = datetime.now().month
    current_year = datetime.now().year
    deviations = []

    budgets = Budget.objects.filter(user=user)
    for budget in budgets:
        total_spent = Expense.objects.filter(
            user=user,
            category=budget.category,
            date__year=current_year,
            date__month=current_month
        ).aggregate(total=Sum("amount"))["total"] or 0

        if total_spent > budget.monthly_limit:
            deviations.append({
                "category": budget.category.name,
                "spent": total_spent,
                "limit": budget.monthly_limit,
                "over_by": total_spent - budget.monthly_limit
            })

    return deviations

# accounts/utils.py

from expenses.models import Expense
from django.db.models import Sum
from accounts.models import Budget
# Define category keywords
from expenses.models import  Expense
import re

CATEGORY_KEYWORDS = {
    "Food": [
        "restaurant", "cafe", "meal", "pizza", "burger", "grocery", "food",
        "snack", "momo", "dinner", "lunch", "breakfast", "fastfood", "sweets",
        "icecream", "drink", "beverage", "coffee", "tea", "juice"
    ],
    "Transport": [
        "bus", "taxi", "uber", "train", "fuel", "petrol", "transport",
        "metro", "taxi fare", "cab", "rickshaw", "auto", "ticket", "flight",
        "car rental", "gas", "parking", "toll", "bike", "bicycle"
    ],
    "Shopping": [
        "mall", "clothes", "shoes", "shopping", "electronics", "gift",
        "accessories", "furniture", "jewelry", "cosmetics", "makeup",
        "apparel", "home decor", "groceries shopping", "stationery", "bags"
    ],
    "Entertainment": [
        "movie", "netflix", "game", "music", "concert", "entertainment",
        "youtube", "youtube premium", "spotify", "netflix subscription",
        "ticket", "cinema", "show", "play", "festival", "amusement park",
        "event", "fun", "hobby"
    ],
    "Health": [
        "hospital", "medicine", "doctor", "health", "pharmacy", "clinic",
        "checkup", "dental", "eye care", "vitamins", "supplements",
        "therapy", "gym", "fitness", "lab test", "hospital bill", "surgery",
        "treatment", "vaccination"
    ],
    "Bills": [
        "electricity", "water", "internet", "bill", "phone bill", "gas bill",
        "mobile recharge", "wifi", "subscription", "rent", "utilities",
        "utility", "heating", "cooling", "electric", "water supply",
        "broadband", "cable", "tv subscription"
    ],
    "Education": [
        "school", "college", "books", "tuition", "education", "stationery",
        "exam", "library", "courses", "online course", "training", "workshop",
        "coaching", "school fees", "college fees", "study material", "learning",
        "notebook", "pen", "project"
    ]
}


def categorize_expense(expense: Expense):
    """
    Automatically assign a Category to the expense based on description.
    Uses keyword matching with partial and multi-word support.
    """
    description = (expense.description or "").lower()
    assigned_category = None
    max_matches = 0

    for category_name, keywords in CATEGORY_KEYWORDS.items():
        matches = sum(1 for kw in keywords if re.search(r'\b' + re.escape(kw) + r'\b', description))
        if matches > max_matches:
            max_matches = matches
            assigned_category, _ = Category.objects.get_or_create(
                user=expense.user, title=category_name
            )

    if assigned_category:
        expense.category = assigned_category
        expense.save()



def get_category(user, title):
    """
    Helper function to get or create a Category object for a user.
    """
    from expenses.models import Category
    category, _ = Category.objects.get_or_create(user=user, title=title)
    return category


def detect_budget_deviation(user):
    deviations = []
    budgets = Budget.objects.filter(user=user)
    for budget in budgets:
        total_spent = Expense.objects.filter(user=user, category=budget.category).aggregate(
            total=Sum('amount')
        )['total'] or 0
        if total_spent > budget.limit:
            deviations.append({
                'category': budget.category.name,
                'limit': budget.limit,
                'spent': total_spent,
                'message': f'Exceeded budget in {budget.category.name}!'
            })
    return deviations


# accounts/utils.py

def safe_float(value):
    """
    Safely convert a value to float.
    Returns 0 if conversion fails.
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0



from incomes.models import Income
from .models import RecurringTransaction
from datetime import date

def process_recurring_transactions():
    """Automatically add recurring transactions for today without duplicates."""
    today = date.today()

    # Get all active recurring transactions
    recurring_transactions = RecurringTransaction.objects.filter(is_active=True)

    for transaction in recurring_transactions:
        user = transaction.user
        amount = transaction.amount
        name = transaction.name.strip().title()  # Normalize name

        # ---- HANDLE INCOME ----
        if transaction.transaction_type == 'Income':
            Income.objects.get_or_create(
                user=user,
                source=name,
                date=today,
                defaults={'amount': amount}
            )

        # ---- HANDLE EXPENSE ----
        elif transaction.transaction_type == 'Expense':
            from expenses.models import Expense
            Expense.objects.get_or_create(
                user=user,
                category=name,
                date=today,
                defaults={'amount': amount}
            )

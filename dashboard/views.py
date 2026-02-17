from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from incomes.models import Income
from expenses.models import Expense
from savings.models import Saving
from debts.models import Debt
from django.db.models import Sum

@login_required
def dashboard(request):
    user = request.user

    # Totals
    total_income = Income.objects.filter(user=user).aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = Expense.objects.filter(user=user).aggregate(Sum('amount'))['amount__sum'] or 0
    total_saving = Saving.objects.filter(user=user).aggregate(Sum('amount'))['amount__sum'] or 0
    total_debt = Debt.objects.filter(user=user).aggregate(Sum('amount'))['amount__sum'] or 0

    # Percentages (for progress bars)
    income_goal = 100000  # replace with user's goal if dynamic
    expense_limit = 50000
    saving_goal = 50000
    debt_limit = 20000

    income_percent = round((total_income / income_goal) * 100, 2) if income_goal else 0
    expense_percent = round((total_expense / expense_limit) * 100, 2) if expense_limit else 0
    saving_percent = round((total_saving / saving_goal) * 100, 2) if saving_goal else 0
    debt_percent = round((total_debt / debt_limit) * 100, 2) if debt_limit else 0

    context = {
        'total_income': total_income,
        'total_expense': total_expense,
        'total_saving': total_saving,
        'total_debt': total_debt,
        'income_percent': income_percent,
        'expense_percent': expense_percent,
        'saving_percent': saving_percent,
        'debt_percent': debt_percent,
        'income_goal': income_goal,
        'expense_limit': expense_limit,
        'saving_goal': saving_goal,
        'debt_limit': debt_limit,
    }
    return render(request, 'dashboard.html', context)

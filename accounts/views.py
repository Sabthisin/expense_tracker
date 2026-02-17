# accounts/views.py

import json
from decimal import Decimal
from datetime import date
from itertools import chain
from django.db.models.functions import TruncMonth
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.db.models import Sum, Q
from django.urls import reverse_lazy
from django.contrib.auth import views as auth_views
from .models import RecurringTransaction
from .models import UserFinancialGoals
from django import forms
# Models
from .models import Budget, Profile
from expenses.models import Expense
from incomes.models import Income
from savings.models import Saving
from debts.models import Debt
from django.db.models import Sum
from datetime import date, timedelta
from django.db.models import Sum, F
from expenses.models import Expense, ExpenseItem, Category
from decimal import Decimal
# Forms
from .forms import (
    ProfileForm,
    SignUpForm,
    BudgetForm,
    LoginForm,
    RecurringTransactionForm,
)

# Utils
from .utils import categorize_expense, detect_budget_deviation, process_recurring_transactions


# -------------------------------
# Utility
# -------------------------------
def safe_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


# -------------------------------
# Authentication Views
# -------------------------------
def signup_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:profile')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            messages.success(request, "Account created successfully! You can now log in.")
            return redirect('accounts:login')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:profile')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username_email = form.cleaned_data['username_email']
            password = form.cleaned_data['password']

            # Try email first
            try:
                user_obj = User.objects.get(email=username_email)
                username = user_obj.username
            except User.DoesNotExist:
                username = username_email

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('accounts:profile')
            else:
                messages.error(request, "Invalid username/email or password")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('accounts:login')


# -------------------------------
# Profile Views
# -------------------------------
@login_required
def profile(request):
    profile = request.user.profile

    dob = profile.date_of_birth if profile.dob_visibility != 'Private' else None
    phone = profile.phone_number if profile.phone_visibility != 'Private' else None

    context = {'profile': profile, 'dob': dob, 'phone': phone}
    return render(request, "accounts/profile.html", context)


@login_required
def edit_profile(request):
    profile_obj, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect("accounts:profile")
        messages.error(request, "Please correct the errors below.")
    else:
        form = ProfileForm(instance=profile_obj)

    return render(request, "accounts/edit_profile.html", {
        "form": form,
        "profile": profile_obj,
        "today": date.today()
    })


@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password updated successfully!")
            return redirect("accounts:profile")
        messages.error(request, "Please correct the errors.")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, "accounts/change_password.html", {"form": form})


@login_required
def delete_profile_picture(request):
    profile = get_object_or_404(Profile, user=request.user)
    if profile.profile_picture:
        profile.profile_picture.delete(save=True)
    return redirect('accounts:edit_profile')




@login_required
def add_budget(request):
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            if not request.user.is_staff:
                budget.user = request.user
            budget.save()
            messages.success(request, "✅ Budget set successfully!")
            return redirect('accounts:budget_status')
    else:
        form = BudgetForm()
        if not request.user.is_staff:
            form.fields.pop('user', None)
    return render(request, 'accounts/add_budget.html', {'form': form})


def budget_status(request):
    budget, created = Budget.objects.get_or_create(user=request.user)
    budget_limit = budget.monthly_limit or Decimal('0.00')

    total_expense = ExpenseItem.objects.filter(
        expense__user=request.user
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    total_expense = Decimal(total_expense)
    deviation = budget_limit - total_expense

    # Determine status and CSS class
    if total_expense > budget_limit:
        status = f"Over Budget by Rs.{total_expense - budget_limit}"
        status_class = "danger"
    elif total_expense > budget_limit / 2:  # safe in Python
        status = f"Approaching Budget"
        status_class = "warning"
    else:
        status = f"Under Budget"
        status_class = "success"

    # Calculate percentage for progress bar
    percent_used = float(total_expense / budget_limit * 100) if budget_limit > 0 else 0
    percent_used = min(percent_used, 100)

    context = {
        "budget_limit": budget_limit,
        "total_expense": total_expense,
        "deviation": deviation,
        "status": status,
        "status_class": status_class,
        "percent_used": percent_used,
    }

    return render(request, "accounts/budget_status.html", context)


def update_budget(request):
    budget, created = Budget.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = BudgetForm(request.POST, instance=budget)
        if form.is_valid():
            form.save()
            return redirect("accounts:budget_status")
    else:
        form = BudgetForm(instance=budget)

    return render(request, "accounts/update_budget.html", {"form": form})



# -------------------------------
# Recurring Transactions
# -------------------------------
@login_required
def add_recurring(request):
    if request.method == 'POST':
        form = RecurringTransactionForm(request.POST)
        if form.is_valid():
            recurring = form.save(commit=False)
            recurring.user = request.user
            recurring.save()
            messages.success(request, "Recurring transaction added successfully!")
            return redirect('accounts:recurring_list')
    else:
        form = RecurringTransactionForm()

    return render(request, 'accounts/add_recurring.html', {'form': form})


@login_required
def recurring_list(request):
    recurring_list = RecurringTransaction.objects.filter(user=request.user).order_by('-start_date')

    return render(request, 'accounts/recurring_list.html', {
        'recurring_list': recurring_list
    })


def edit_recurring_transaction(request, pk):
    recurring = get_object_or_404(RecurringTransaction, pk=pk, user=request.user)
    if request.method == 'POST':
        form = RecurringTransactionForm(request.POST, instance=recurring)
        if form.is_valid():
            form.save()
            return redirect('accounts:recurring_list')
    else:
        form = RecurringTransactionForm(instance=recurring)

    return render(request, 'accounts/edit_recurring.html', {'form': form})


def delete_recurring_transaction(request, pk):
    recurring = get_object_or_404(RecurringTransaction, pk=pk, user=request.user)
    if request.method == 'POST':
        recurring.delete()
        return redirect('accounts:recurring_list')
    return render(request, 'accounts/delete_recurring.html', {'recurring': recurring})

# -------------------------------
# Dashboard
# -------------------------------
# Adjust path if needed


def safe_float(value):
    return float(value) if value is not None else 0.0


@login_required
def dashboard_view(request):
    user = request.user

    # === Get or create user's financial goals ===
    goals, created = UserFinancialGoals.objects.get_or_create(
        user=user,
        defaults={
            'monthly_income_goal': 100000,
            'monthly_expense_limit': 60000,
            'monthly_saving_goal': 30000,
            'max_debt_limit': 20000,
        }
    )

    # === Raw Totals ===
    total_income = safe_float(Income.objects.filter(user=user).aggregate(t=Sum('amount'))['t'])
    total_expense = safe_float(ExpenseItem.objects.filter(expense__user=user).aggregate(t=Sum('amount'))['t'])
    total_saving = safe_float(Saving.objects.filter(user=user).aggregate(t=Sum('amount'))['t'])
    total_debt = safe_float(Debt.objects.filter(user=user).aggregate(t=Sum('amount'))['t'])

    # Add recurring income
    recurring_income = safe_float(
        RecurringTransaction.objects.filter(user=user, transaction_type='Income', is_active=True)
        .aggregate(t=Sum('amount'))['t']
    )
    total_income += recurring_income

    # === Use USER-DEFINED goals ===
    INCOME_GOAL = float(goals.monthly_income_goal)
    EXPENSE_LIMIT = float(goals.monthly_expense_limit)
    SAVING_GOAL = float(goals.monthly_saving_goal)
    DEBT_LIMIT = float(goals.max_debt_limit)

    # === Calculate Percentages ===
    def calc_percent(amount, goal):
        if goal <= 0:
            return 0.0
        percent = (amount / goal) * 100
        return min(round(percent, 1), 100.0)  # Cap at 100%

    income_percent = calc_percent(total_income, INCOME_GOAL)
    expense_percent = calc_percent(total_expense, EXPENSE_LIMIT)
    saving_percent = calc_percent(total_saving, SAVING_GOAL)
    debt_percent = calc_percent(total_debt, DEBT_LIMIT)

    # === AI Prediction (unchanged) ===
    monthly_expenses = ExpenseItem.objects.filter(expense__user=user)\
        .annotate(month=TruncMonth('expense__date'))\
        .values('month')\
        .annotate(total=Sum('amount'))\
        .order_by('month')
    
    values = [safe_float(m['total']) for m in monthly_expenses]
    predicted = values[-1] if values else 0
    if len(values) >= 2:
        # Simple trend
        predicted = sum(values[-3:]) / len(values[-3:]) * 1.05  # 5% growth estimate

    predicted_expense = round(predicted, 0)

    # === Chart Data ===
    chart_labels = ['Income', 'Expense', 'Savings', 'Debt']
    chart_data = [income_percent, expense_percent, saving_percent, debt_percent]

    context = {
        'total_income': round(total_income, 2),
        'total_expense': round(total_expense, 2),
        'total_saving': round(total_saving, 2),
        'total_debt': round(total_debt, 2),

        'income_percent': income_percent,
        'expense_percent': expense_percent,
        'saving_percent': saving_percent,
        'debt_percent': debt_percent,

        'predicted_expense': int(predicted_expense),

        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),

        # Optional: Show current goals in template
        'goals': goals,
    }

    return render(request, 'accounts/dashboard.html', context)

# accounts/views.py


# Form for setting goals
class FinancialGoalsForm(forms.ModelForm):
    class Meta:
        model = UserFinancialGoals
        fields = [
            'monthly_income_goal',
            'monthly_expense_limit',
            'monthly_saving_goal',
            'max_debt_limit'
        ]
        widgets = {
            'monthly_income_goal': forms.NumberInput(attrs={'class': 'form-control', 'step': '1000', 'min': '0'}),
            'monthly_expense_limit': forms.NumberInput(attrs={'class': 'form-control', 'step': '1000', 'min': '0'}),
            'monthly_saving_goal': forms.NumberInput(attrs={'class': 'form-control', 'step': '1000', 'min': '0'}),
            'max_debt_limit': forms.NumberInput(attrs={'class': 'form-control', 'step': '1000', 'min': '0'}),
        }
        labels = {
            'monthly_income_goal': 'Target Monthly Income (Rs.)',
            'monthly_expense_limit': 'Maximum Monthly Expense (Rs.)',
            'monthly_saving_goal': 'Monthly Savings Goal (Rs.)',
            'max_debt_limit': 'Maximum Acceptable Debt (Rs.)',
        }

@login_required
def set_financial_goals(request):
    goals, created = UserFinancialGoals.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = FinancialGoalsForm(request.POST, instance=goals)
        if form.is_valid():
            form.save()
            messages.success(request, "Your financial goals have been updated successfully!")
            return redirect('accounts:dashboard')
    else:
        form = FinancialGoalsForm(instance=goals)

    return render(request, 'accounts/set_goals.html', {
        'form': form,
        'goals': goals
    })
# -------------------------------
# Admin Views
# -------------------------------
def admin_only(user):
    return user.is_superuser


@login_required
@user_passes_test(admin_only)
def user_list(request):
    users = User.objects.all()
    return render(request, 'accounts/user_list.html', {'users': users})


@login_required
@user_passes_test(admin_only)
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.delete()
        messages.success(request, "🗑️ User deleted successfully!")
        return redirect('accounts:user_list')
    return render(request, 'accounts/confirm_delete.html', {'user': user})

def recurring_list(request):
    recurring_list = RecurringTransaction.objects.filter(user=request.user)
    return render(request, 'accounts/recurring_list.html', {'recurring_list': recurring_list})
# -------------------------------
# Password Reset
# -------------------------------
class CustomPasswordResetView(auth_views.PasswordResetView):
    template_name = 'registration/password_reset_form.html'
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    success_url = reverse_lazy('accounts:password_reset_done')


class CustomPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'registration/password_reset_done.html'


class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'registration/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')


class CustomPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'registration/password_reset_complete.html'

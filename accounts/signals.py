
# accounts/signals.py
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Profile  # import Expense model
from accounts.services.budget_service import update_budget_spent   # import the function
# Automatically create Profile when a new User is created
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import  Budget
from expenses.models import ExpenseItem

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()


@receiver(post_save, sender=ExpenseItem)
def update_budget_on_expense(sender, instance, created, **kwargs):
    if created:
        # Loop through all categories assigned to this item
        for cat in instance.categories.all():
            budget = Budget.objects.filter(user=instance.expense.user, category=cat).first()
            if budget:
                budget.amount_spent += instance.amount
                budget.save()


@receiver(post_delete, sender=ExpenseItem)
def reduce_budget_on_delete(sender, instance, **kwargs):
    for cat in instance.categories.all():
        budget = Budget.objects.filter(user=instance.expense.user, category=cat).first()
        if budget:
            budget.amount_spent -= instance.amount
            budget.save()
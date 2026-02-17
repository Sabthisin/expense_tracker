from django.db import models
from django.contrib.auth.models import User  # our smart categorizer
from accounts.models import Category


# models.py
class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    date = models.DateField()
    # remove total_amount field

    @property
    def total_amount(self):
        return sum(item.amount for item in self.items.all())

    def __str__(self):
        return f"{self.user.username} - {self.date}"

class ExpenseItem(models.Model):
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name='items')
    title = models.CharField(max_length=200)
    amount = models.FloatField()
    categories = models.ManyToManyField(Category, blank=True)

    def __str__(self):
        return self.title
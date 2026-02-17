from django.db import models
from django.contrib.auth.models import User

class Debt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lender = models.CharField(max_length=255, verbose_name="Creditor (Who you must pay)")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    is_paid = models.BooleanField(default=False)
    

    def __str__(self):
        return f"{self.lender} - {self.amount} ({'Paid' if self.is_paid else 'Unpaid'})"


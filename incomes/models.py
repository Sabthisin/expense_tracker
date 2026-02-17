from django.db import models
from django.contrib.auth.models import User
from datetime import date

class Income(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    source = models.CharField(max_length=100)  # match the DB column
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=date.today)

    def __str__(self):
        return f"{self.source} - {self.amount}"


from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

# ----------------------
# CATEGORY MODEL
# ----------------------


class Category(models.Model):
    name = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return self.name


# accounts/models.py



class Budget(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    monthly_limit = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.user.username}'s Budget"


 
# ----------------------
# PROFILE MODEL


class Profile(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    bio = models.TextField(max_length=300, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    address = models.TextField(blank=True)
    website = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)




    VISIBILITY_CHOICES = (
        ('Public', 'Public'),
        ('Private', 'Private'),
    )
    dob_visibility = models.CharField(max_length=7, choices=VISIBILITY_CHOICES, default='Private')
    phone_visibility = models.CharField(max_length=7, choices=VISIBILITY_CHOICES, default='Private')

    def __str__(self):
        return f"{self.user.username}'s Profile"
 


from django.db import models
from django.contrib.auth.models import User
from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError

class RecurringTransaction(models.Model):

    TRANSACTION_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    start_date = models.DateField()
    next_run = models.DateField()
    is_active = models.BooleanField(default=True)

    # -------------------------
    # VALIDATION (1 month rule)
    # -------------------------
    def clean(self):
        expected_next = self.start_date + relativedelta(months=1)
        if self.next_run != expected_next:
            raise ValidationError(
                {"next_run": "Next run date must be exactly 1 month after the start date."}
            )

    # -------------------------
    # AUTO SET next_run ON CREATE
    # -------------------------
    def save(self, *args, **kwargs):
        # On first create, enforce 1 month rule even if user tries to skip
        if not self.id:  
            self.next_run = self.start_date + relativedelta(months=1)
        self.clean()  # ensure validation runs
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.user.username} ({self.transaction_type})"



# accounts/models.py  (or create a new app: goals/models.py)

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

class UserFinancialGoals(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='financial_goals')
    
    monthly_income_goal = models.DecimalField(
        max_digits=12, decimal_places=2,
        default=100000.00,
        validators=[MinValueValidator(0)],
        help_text="Your target monthly income (Rs.)"
    )
    monthly_expense_limit = models.DecimalField(
        max_digits=12, decimal_places=2,
        default=60000.00,
        validators=[MinValueValidator(0)],
        help_text="Maximum allowed monthly expense (Rs.)"
    )
    monthly_saving_goal = models.DecimalField(
        max_digits=12, decimal_places=2,
        default=30000.00,
        validators=[MinValueValidator(0)],
        help_text="Target monthly savings (Rs.)"
    )
    max_debt_limit = models.DecimalField(
        max_digits=12, decimal_places=2,
        default=20000.00,
        validators=[MinValueValidator(0)],
        help_text="Maximum acceptable total debt (Rs.)"
    )

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Financial Goal"
        verbose_name_plural = "Financial Goals"

    def __str__(self):
        return f"{self.user.username}'s Financial Goals"
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Profile, Budget, Category

# ---------------------
# Inline profile display in User admin
# ---------------------
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'

# Extend UserAdmin
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    filter_horizontal = ('groups', 'user_permissions',)

# Replace default User admin with custom one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# ---------------------
# Budget admin
# ---------------------

from django import forms
from django.core.exceptions import ValidationError

# -------------------------------
#  Custom Admin Form (Validation)
# -------------------------------
class BudgetAdminForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = "__all__"

    def clean_monthly_limit(self):
        limit = self.cleaned_data.get("monthly_limit")
        if limit is None or limit <= 0:
            raise ValidationError("Monthly limit must be greater than zero.")
        return limit

    def clean_user(self):
        user = self.cleaned_data.get("user")

        # Prevent duplicate budget for same user
        qs = Budget.objects.filter(user=user)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise ValidationError("This user already has a budget assigned.")
        return user


# -------------------------------
#  Admin Settings for Budget
# -------------------------------
@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    form = BudgetAdminForm

    list_display = ("user", "monthly_limit")
    search_fields = ("user__username",)
    list_filter = ("user",)

    def save_model(self, request, obj, form, change):
        # Auto-assign budget's user if needed (optional)
        if not obj.pk and not request.user.is_staff:
            obj.user = request.user
        super().save_model(request, obj, form, change)



# ---------------------
# Category admin
# ---------------------
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


# accounts/admin.py or goals/admin.py
from django.contrib import admin
from .models import UserFinancialGoals

@admin.register(UserFinancialGoals)
class UserFinancialGoalsAdmin(admin.ModelAdmin):
    list_display = ('user', 'monthly_income_goal', 'monthly_expense_limit', 'monthly_saving_goal', 'max_debt_limit')
    list_editable = ('monthly_income_goal', 'monthly_expense_limit', 'monthly_saving_goal', 'max_debt_limit')
    search_fields = ('user__username', 'user__email')
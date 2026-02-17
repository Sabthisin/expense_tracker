from django.contrib import admin
from .models import Debt

@admin.register(Debt)
class DebtAdmin(admin.ModelAdmin):
    list_display = ('lender', 'amount', 'due_date', 'is_paid', 'user')
    list_filter = ('due_date', 'is_paid', 'user')

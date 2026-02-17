from django.contrib import admin
from .models import  ExpenseItem

class ExpenseItemInline(admin.TabularInline):
    model = ExpenseItem.categories.through  # ManyToMany through table
    extra = 0

@admin.register(ExpenseItem)
class ExpenseItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'amount', 'expense')
    filter_horizontal = ('categories',)

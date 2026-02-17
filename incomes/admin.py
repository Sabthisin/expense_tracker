from django.contrib import admin
from .models import Income

class IncomeAdmin(admin.ModelAdmin):
    list_display = ['source', 'amount', 'date']  # replace 'source' with 'title'

admin.site.register(Income, IncomeAdmin)

    

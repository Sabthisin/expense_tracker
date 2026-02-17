from django.contrib import admin
from .models import Saving

class SavingAdmin(admin.ModelAdmin):
    list_display = ('user', 'goal', 'amount', 'date')  # all must exist on model
    list_filter = ('user', 'date')

admin.site.register(Saving, SavingAdmin)

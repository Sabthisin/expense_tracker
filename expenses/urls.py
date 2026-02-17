from django.urls import path
from . import views

app_name = 'expenses'

urlpatterns = [
    path('', views.expense_list, name='expense_list'),
    path('add/', views.add_expense, name='add_expense'),
    path('update/<int:expense_id>/', views.update_expense, name='update_expense'),
    path('delete/<int:expense_id>/', views.delete_expense, name='delete_expense'),
    path('admin/list/', views.admin_expense_list, name='admin_expense_list'),
    path('admin/update/<int:expense_id>/', views.admin_update_expense, name='admin_update_expense'),
    path('download/expenses/', views.download_expenses_pdf, name='download_expenses_pdf'),
]

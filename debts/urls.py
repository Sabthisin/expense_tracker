# debts/urls.py
from django.urls import path
from . import views

app_name = 'debts'

urlpatterns = [
    path('', views.debt_list, name='debt_list'),
    path('add_debt/', views.add_debt, name='add_debt'),
    path('update_debt/<int:id>/', views.update_debt, name='update_debt'),   
    path('delete_debt/<int:debt_id>/', views.delete_debt, name='delete_debt'),
    path('download/pdf/', views.download_debt_pdf, name='download_debt_pdf'), 
]

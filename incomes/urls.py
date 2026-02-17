from django.urls import path
from . import views

app_name = 'incomes'
urlpatterns = [
    path('', views.income_list, name='income_list'),   # /incomes/
    path('add/', views.add_income, name='add_income'), # /incomes/add/
    path('update/<int:income_id>/', views.update_income, name='update_income'),
    path('delete/<int:id>/', views.delete_income, name='delete_income'),
    path('download/pdf/', views.download_income_pdf, name='download_income_pdf'),
]

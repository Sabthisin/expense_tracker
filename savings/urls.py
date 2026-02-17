
from django.urls import path
from . import views


app_name = 'savings'

urlpatterns = [
    path('savings/', views.saving_list, name='saving_list'),
    path('savings/add/', views.add_saving, name='add_saving'),
    path('savings/update/<int:id>/', views.update_saving, name='update_saving'),
    path('savings/delete/<int:id>/', views.delete_saving, name='delete_saving'),
    path('download/pdf/', views.download_savings_pdf, name='download_savings_pdf'),
]


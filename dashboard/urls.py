from django.urls import path
from accounts import views

app_name = 'dashboard_app'

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
]


"""
URL configuration for expense_tracker project.
"""

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    path('admin/logout/', LogoutView.as_view(next_page='/admin/login/'), name='admin_logout'),

    # Accounts app
    path('accounts/', include('accounts.urls', namespace='accounts')),  # your custom URLs

    # Built-in Django auth
    path('accounts/', include('django.contrib.auth.urls')),  # handles login/logout/password reset

    # Other apps
    path('expenses/', include('expenses.urls')),
    path('incomes/', include('incomes.urls')),
    path('savings/', include('savings.urls')),
    path('debts/', include('debts.urls')),
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),

    # Default route → always redirect to Login page
    path('', lambda request: redirect('accounts:login'), name='root_redirect'),
]

# Media files
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

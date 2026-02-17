from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # --- User Authentication ---
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # --- Profile Management ---
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/delete_photo/', views.delete_profile_picture, name='delete_profile_picture'),

    # --- Budget Management ---
    path('budget-status/', views.budget_status, name='budget_status'),
    path('update-budget/', views.update_budget, name='update_budget'),
    # --- Dashboard / Expense Tracker ---
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # --- Password Change (requires login) ---
    path(
        'password_change/',
        auth_views.PasswordChangeView.as_view(
            template_name='registration/password_change_form.html',
            success_url='/accounts/password_change/done/'
        ),
        name='password_change'
    ),
    path(
        'password_change/done/',
        auth_views.PasswordChangeDoneView.as_view(
            template_name='registration/password_change_done.html'
        ),
        name='password_change_done'
    ),
    # --- Password Reset (Forgot Password) using Username ---
    path('password-reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('recurring/add/', views.add_recurring, name='add_recurring'),
    path('recurring/edit/<int:pk>/', views.edit_recurring_transaction, name='edit_recurring'),
    path('recurring/delete/<int:pk>/', views.delete_recurring_transaction, name='delete_recurring'),
    path('recurring/list/', views.recurring_list, name='recurring_list'),
    path('set-goals/', views.set_financial_goals, name='set_goals'),
]

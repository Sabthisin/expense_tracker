# accounts/services/alert_service.py

from django.core.mail import send_mail

def send_budget_alert(user, category, limit, spent, status):
    subject = f"Budget Alert: {category} - {status}"

    message = (
        f"Hello {user.username},\n\n"
        f"Your spending status for '{category}' is now: {status}\n"
        f"-------------------------------------------------\n"
        f"Budget Limit: Rs. {limit}\n"
        f"Spent: Rs. {spent}\n"
        f"Status: {status}\n"
        f"-------------------------------------------------\n\n"
        f"Please manage your expenses wisely.\n\n"
        f"Regards,\n"
        f"Expense Tracker System"
    )

    send_mail(
        subject,
        message,
        'your_email@gmail.com',     # FROM EMAIL
        [user.email],               # TO EMAIL
        fail_silently=True,
    )

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from  accounts.models import  Category
from .models import Expense
from .forms import ExpenseForm
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from .models import Expense, ExpenseItem
from .services.category_service import detect_categories 
from .parser import parse_and_categorize

# -------------------------
# Expense Views
# -------------------------
@login_required
def expense_list(request):
    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    return render(request, 'expenses/expense_list.html', {'expenses': expenses})

  # Your parser function
@login_required
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()

            # Parse description and create ExpenseItems
            items_data = parse_and_categorize(expense.description)
            for item_data in items_data:
                item = ExpenseItem.objects.create(
                    expense=expense,
                    title=item_data['title'],
                    amount=item_data['amount']
                )
                # Assign categories (many-to-many)
                for cat_name in item_data['categories']:
                    category, _ = Category.objects.get_or_create(user=request.user, name=cat_name)
                    item.categories.add(category)

            messages.success(request, "✅ Expense added successfully!")
            return redirect('expenses:expense_list')
        messages.error(request, "⚠️ Please correct the errors below.")
    else:
        form = ExpenseForm()

    return render(request, 'expenses/add_expense.html', {'form': form})

@login_required
def update_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, user=request.user)

    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            expense = form.save()

            # Delete old items
            expense.items.all().delete()

            # Parse description and recreate ExpenseItems
            items_data = parse_and_categorize(expense.description)
            for item_data in items_data:
                item = ExpenseItem.objects.create(
                    expense=expense,
                    title=item_data['title'],
                    amount=item_data['amount']
                )
                for cat_name in item_data['categories']:
                    category, _ = Category.objects.get_or_create(user=request.user, name=cat_name)
                    item.categories.add(category)

            messages.success(request, "✅ Expense updated successfully!")
            return redirect('expenses:expense_list')
        messages.error(request, "⚠️ Please correct the errors below.")
    else:
        form = ExpenseForm(instance=expense)

    return render(request, 'expenses/update_expense.html', {'form': form, 'expense': expense})


@login_required
def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, user=request.user)
    if request.method == "POST":
        expense.delete()
        messages.success(request, "✅ Expense deleted successfully!")
        return redirect('expenses:expense_list')
    return render(request, 'expenses/delete_expense.html', {'expense': expense})

# Admin views
# -------------------------
@staff_member_required
def admin_expense_list(request):
    expenses = Expense.objects.all().order_by('-date')
    return render(request, 'expenses/admin_expense_list.html', {'expenses': expenses})

@staff_member_required
def admin_update_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)

    if request.method == "POST":
        form = ExpenseForm(request.POST, instance=expense)

        if form.is_valid():
            expense = form.save(commit=False)
            expense.save()
            form.save_m2m()

            # Auto categorize
            cat_names = detect_categories(expense.description)
            for cat_name in cat_names:
                category_obj, _ = Category.objects.get_or_create(name=cat_name)
                expense.categories.add(category_obj)

            messages.success(request, "✅ Expense updated successfully!")
            return redirect('expenses:admin_expense_list')

    else:
        form = ExpenseForm(instance=expense)

    return render(request, 'expenses/update_expense.html', {'form': form, 'expense': expense})




# -----------------------------
# PDF Download
# -----------------------------

@login_required
def download_expenses_pdf(request):
    # Get all expenses for the user
    expenses = Expense.objects.filter(user=request.user).order_by('-date')

    if not expenses.exists():
        return HttpResponse("⚠️ No expenses available to download.", status=403)

    # Create the HttpResponse object with PDF headers
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="expenses.pdf"'

    # Create the PDF object
    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # Title
    p.setFont("Helvetica-Bold", 16)
    p.drawString(200, height - 50, "Expense List")

    # Table headers
    p.setFont("Helvetica-Bold", 12)
    y = height - 80
    p.drawString(50, y, "Title")
    p.drawString(200, y, "Categories")
    p.drawString(350, y, "Amount")
    p.drawString(450, y, "Date")
    y -= 20

    # Table content
    p.setFont("Helvetica", 12)
    for expense in expenses:
        for item in expense.items.all():
            # Join multiple categories
            category_names = ", ".join([c.name for c in item.categories.all()]) or "Other"

            p.drawString(50, y, item.title)
            p.drawString(200, y, category_names)
            p.drawString(350, y, str(item.amount))
            p.drawString(450, y, expense.date.strftime("%b %d, %Y"))
            y -= 20

            # Create a new page if we run out of space
            if y < 50:
                p.showPage()
                y = height - 50
                p.setFont("Helvetica", 12)

    p.showPage()
    p.save()
    return response
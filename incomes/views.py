# incomes/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Income
from .forms import IncomeForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from django.contrib import messages
# -------------------------
# List all incomes for logged-in user
# -------------------------
@login_required
def income_list(request):
    incomes = Income.objects.filter(user=request.user).order_by('-date')
    return render(request, 'incomes/income_list.html', {'incomes': incomes})

# -------------------------
# Add new income
# -------------------------

def add_income(request):
    if request.method == 'POST':
        form = IncomeForm(request.POST)
        if form.is_valid():
            income = form.save(commit=False)
            income.user = request.user
            income.save()
            messages.success(request, "Income added successfully!")
            return redirect('incomes:income_list')
    else:
        form = IncomeForm()
    
    return render(request, 'incomes/add_income.html', {'form': form})

# -------------------------
# Update existing income
# -------------------------
@login_required
def update_income(request, income_id):
    income = get_object_or_404(Income, id=income_id, user=request.user)
    if request.method == 'POST':
        form = IncomeForm(request.POST, instance=income)
        if form.is_valid():
            form.save()
            return redirect('incomes:income_list')
    else:
        form = IncomeForm(instance=income)
    return render(request, 'incomes/update_income.html', {'form': form})

# -------------------------
# Delete existing income
# -------------------------
@login_required
def delete_income(request, id):
    income = get_object_or_404(Income, id=id, user=request.user)
    if request.method == 'POST':
        income.delete()
        return redirect('incomes:income_list')
    return render(request, 'incomes/delete_income.html', {'income': income})


@login_required(login_url='accounts:login')
def download_income_pdf(request):
    incomes = Income.objects.filter(user=request.user).order_by('-date')
    if not incomes.exists():
        messages.error(request, "No income available to download!")
        return render(request, 'income/income_list.html', {'incomes': incomes})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="income.pdf"'
    p = canvas.Canvas(response)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(200, 800, "Income List")

    y = 760
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Source")
    p.drawString(200, y, "Amount")
    p.drawString(350, y, "Date")

    p.setFont("Helvetica", 12)
    y -= 25
    for income in incomes:
        p.drawString(50, y, income.source)
        p.drawString(200, y, str(income.amount))
        p.drawString(350, y, income.date.strftime("%b %d, %Y"))
        y -= 20
        if y < 50:
            p.showPage()
            y = 800

    p.showPage()
    p.save()
    return response

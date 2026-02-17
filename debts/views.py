from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from .models import Debt
from .forms import DebtForm

# --- Debt List View ---
@login_required(login_url='accounts:login')
def debt_list(request):
    debts = Debt.objects.filter(user=request.user).order_by('-due_date')
    return render(request, 'debts/debt_list.html', {'debts': debts})

# --- Add Debt ---
@login_required(login_url='accounts:login')
def add_debt(request):
    if request.method == "POST":
        form = DebtForm(request.POST)
        if form.is_valid():
            debt = form.save(commit=False)
            debt.user = request.user
            debt.save()
            return redirect('debts:debt_list')
    else:
        form = DebtForm()
    return render(request, 'debts/add_debt.html', {'form': form})

# --- Update Debt ---
@login_required(login_url='accounts:login')
def update_debt(request, id):
    debt = get_object_or_404(Debt, id=id, user=request.user)
    if request.method == "POST":
        form = DebtForm(request.POST, instance=debt)
        if form.is_valid():
            form.save()
            return redirect('debts:debt_list')
    else:
        form = DebtForm(instance=debt)
    return render(request, 'debts/update_debt.html', {'form': form})

# --- Delete Debt ---
@login_required(login_url='accounts:login')
def delete_debt(request, debt_id):
    debt = get_object_or_404(Debt, id=debt_id, user=request.user)

    if request.method == "POST":
        debt.delete()
        return redirect('debts:debt_list')
    # Render confirmation page
    return render(request, 'debts/delete_debt.html', {'debt': debt})
# --- Download Debt PDF ---


@login_required(login_url='accounts:login')
def download_debt_pdf(request):
    debts = Debt.objects.filter(user=request.user).order_by('-due_date')
    if not debts.exists():
        messages.error(request, "No debts available to download!")
        return redirect('debt:debt_list')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="debts.pdf"'

    p = canvas.Canvas(response)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(200, 800, "Debt List")

    y = 760
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Lender")
    p.drawString(200, y, "Amount")
    p.drawString(300, y, "Due Date")
    p.drawString(400, y, "Is Paid")

    p.setFont("Helvetica", 12)
    y -= 25
    for debt in debts:
        p.drawString(50, y, str(debt.lender))
        p.drawString(200, y, str(debt.amount))
        p.drawString(300, y, debt.due_date.strftime("%b %d, %Y"))
        p.drawString(400, y, "Yes" if debt.is_paid else "No")
        y -= 20
        if y < 50:
            p.showPage()
            y = 800

    p.showPage()
    p.save()
    return response

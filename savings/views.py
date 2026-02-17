from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from .models import Saving
from .forms import SavingForm

# --- List Savings ---
@login_required(login_url='login')
def saving_list(request):
    savings = Saving.objects.filter(user=request.user).order_by('-date')
    return render(request, 'savings/saving_list.html', {'savings': savings})

# --- Add Saving ---
@login_required(login_url='login')
def add_saving(request):
    if request.method == 'POST':
        form = SavingForm(request.POST)
        if form.is_valid():
            saving = form.save(commit=False)
            saving.user = request.user  # attach logged-in user
            saving.save()
            return redirect('savings:saving_list')
    else:
        form = SavingForm()
    return render(request, 'savings/add_saving.html', {'form': form})

# --- Update Saving ---
@login_required(login_url='login')
def update_saving(request, id):
    saving = get_object_or_404(Saving, id=id, user=request.user)
    if request.method == "POST":
        form = SavingForm(request.POST, instance=saving)
        if form.is_valid():
            form.save()
            return redirect('savings:saving_list')
    else:
        form = SavingForm(instance=saving)
    return render(request, 'savings/update_saving.html', {'form': form})

# --- Delete Saving ---
@login_required(login_url='login')
def delete_saving(request, id):
    saving = get_object_or_404(Saving, id=id, user=request.user)
    if request.method == "POST":
        saving.delete()
        return redirect('savings:saving_list')
    return render(request, 'savings/delete_saving.html', {'saving': saving})

# --- Download Savings PDF ---
@login_required(login_url='login')
def download_savings_pdf(request):
    savings = Saving.objects.filter(user=request.user).order_by('-date')

    if not savings.exists():
        messages.error(request, "No savings available to download!")
        return redirect('savings:saving_list')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="savings.pdf"'

    p = canvas.Canvas(response)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(200, 800, "Savings List")

    y = 760
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Amount")
    p.drawString(200, y, "Description")
    p.drawString(400, y, "Date")

    p.setFont("Helvetica", 12)
    y -= 25
    for saving in savings:
        p.drawString(50, y, str(saving.amount))
        p.drawString(200, y, saving.description if saving.description else "-")
        p.drawString(400, y, saving.date.strftime("%b %d, %Y"))
        y -= 20
        if y < 50:
            p.showPage()
            y = 800

    p.showPage()
    p.save()
    return response

from django import forms
from .models import Debt

class DebtForm(forms.ModelForm):
    class Meta:
        model = Debt
        fields = ['lender', 'amount', 'due_date', 'is_paid']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }




    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 🔥 Add your custom label here
        self.fields['lender'].label = "Creditor (To whom you owe money)"
    # Validate lender → only letters and spaces
    def clean_lender(self):
        lender = self.cleaned_data.get('lender')

        if not lender:
            raise forms.ValidationError("Lender name is required.")

        if not lender.replace(" ", "").isalpha():
            raise forms.ValidationError("Lender name must contain only letters.")

        return lender

    # Validate positive amount
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')

        if amount is not None and amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")

        return amount

    # Validate due date exists (future dates allowed)
    def clean_due_date(self):
        due_date = self.cleaned_data.get('due_date')

        if not due_date:
            raise forms.ValidationError("Please choose a due date.")

        return due_date

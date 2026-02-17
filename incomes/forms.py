from django import forms
from .models import Income
import re

class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ['source', 'amount', 'date']  # updated field names
        widgets = {
            'source': forms.TextInput(attrs={'placeholder': 'Income source'}),
            'amount': forms.NumberInput(attrs={'placeholder': 'Enter amount'}),
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    # Validate source: letters and spaces only
    def clean_source(self):
        source = self.cleaned_data.get('source')

        # Check minimum length
        if len(source) < 3:
            raise forms.ValidationError("Source must be at least 3 characters long.")

        # Ensure only letters and spaces
        if not re.fullmatch(r'[A-Za-z ]+', source):
            raise forms.ValidationError("Source must contain only letters and spaces.")

        return source

    # Validate amount: must be positive
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")
        return amount

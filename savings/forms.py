from django import forms
from .models import Saving

class SavingForm(forms.ModelForm):
    class Meta:
        model = Saving
        fields = ['amount', 'goal', 'date', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    # Validate positive amount
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is not None and amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")
        return amount

    # Validate goal length
    def clean_goal(self):
        goal = self.cleaned_data.get('goal')

        if not goal:
            raise forms.ValidationError("Goal field cannot be empty.")

    # Allow only digits
        if not goal.isdigit():
            raise forms.ValidationError("Goal must contain only numbers.")

        return goal


    # Validate date exists (future date allowed)
    def clean_date(self):
        date = self.cleaned_data.get('date')
        if not date:
            raise forms.ValidationError("Please select a valid date.")
        return date

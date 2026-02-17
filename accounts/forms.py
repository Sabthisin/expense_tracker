# accounts/forms.py

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordResetForm
from django.core.exceptions import ValidationError
from datetime import date
from .models import Profile, Budget
from .models import RecurringTransaction

# -----------------------------
# LOGIN FORM
# -----------------------------
class LoginForm(forms.Form):
    username_email = forms.CharField(
        label="Username or Email",
        widget=forms.TextInput(attrs={'placeholder': 'Email or Username', 'class': 'form-control'})
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )


# -----------------------------
# SIGNUP FORM
# -----------------------------
class SignUpForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        min_length=6
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email is already registered.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords do not match.")


# -----------------------------
# PROFILE FORM
# -----------------------------
class CustomClearableFileInput(forms.ClearableFileInput):
    clear_checkbox_label = ''  
    initial_text = ''          
    input_text = 'Change'      
    template_name = 'django/forms/widgets/input.html'

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'full_name', 'profile_picture', 'bio', 'phone_number', 'phone_visibility',
            'date_of_birth', 'dob_visibility', 'gender', 'address', 'website', 'linkedin', 'twitter'
        ]
        widgets = {
            'profile_picture': CustomClearableFileInput(attrs={'class': 'form-control'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'linkedin': forms.URLInput(attrs={'class': 'form-control'}),
            'twitter': forms.URLInput(attrs={'class': 'form-control'}),
            'dob_visibility': forms.Select(attrs={'class': 'form-select'}),
            'phone_visibility': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_date_of_birth(self):
        dob = self.cleaned_data.get('date_of_birth')
        if dob and dob > date.today():
            raise forms.ValidationError("Date of Birth cannot be in the future.")
        return dob


# -----------------------------
# EDIT PROFILE FORM
# -----------------------------
class EditProfileForm(forms.ModelForm):
    dob = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Date of Birth'
    )
    email = forms.EmailField(required=True)
    username = forms.CharField(min_length=3)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'dob']

    def clean_dob(self):
        dob = self.cleaned_data['dob']
        today = date.today()
        if dob > today:
            raise forms.ValidationError('Date of birth cannot be in the future.')
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        if age < 10:
            raise forms.ValidationError('You must be at least 10 years old.')
        return dob

    def clean_username(self):
        username = self.cleaned_data['username']
        user_id = self.instance.id
        if User.objects.exclude(pk=user_id).filter(username=username).exists():
            raise forms.ValidationError('This username is already taken.')
        if len(username) < 3:
            raise forms.ValidationError('Username must be at least 3 characters long.')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        user_id = self.instance.id
        if User.objects.exclude(pk=user_id).filter(email=email).exists():
            raise forms.ValidationError('This email is already used.')
        return email


# -----------------------------
# EXPENSE FORM
# -----------------------------



# -----------------------------
# BUDGET FORM
# -----------------------------



class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['monthly_limit']

        widgets = {
            'monthly_limit': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Monthly Budget Limit'
            })
        }


# -----------------------------
# RECURRING TRANSACTION FORM
# -----------------------------
# accounts/forms.py

from .models import RecurringTransaction
from datetime import date

class RecurringTransactionForm(forms.ModelForm):
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=date.today,
        label="Start Date"
    )

    next_run = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=date.today,
        label="Next Run Date"
    )

    class Meta:
        model = RecurringTransaction
        fields = [
            'name',
            'amount',
            'transaction_type',
            'start_date',
            'next_run',
            'is_active'
        ]

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Transaction Name'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Amount'}),
            'transaction_type': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'next_run': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")
        return amount

    def clean_next_run(self):
        start_date = self.cleaned_data.get('start_date')
        next_run = self.cleaned_data.get('next_run')
        if next_run < start_date:
            raise forms.ValidationError("Next run date cannot be before start date.")
        return next_run



# -----------------------------
# USERNAME RESET FORM
# -----------------------------
class UsernamePasswordResetForm(forms.Form):
    username = forms.CharField(max_length=150, label="Username")

    def get_users_email(self):
        username = self.cleaned_data["username"]
        try:
            user = User.objects.get(username=username)
            if user.email:
                return [user.email]
        except User.DoesNotExist:
            return []
        return []

    def save(self, **kwargs):
        email_addresses = self.get_users_email()
        if email_addresses:
            form = PasswordResetForm({"email": email_addresses[0]})
            if form.is_valid():
                form.save(**kwargs)

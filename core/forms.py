from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class UserSignupForm(UserCreationForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"class": "input", "placeholder": "Create a strong password"})
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={"class": "input", "placeholder": "Re-enter password"})
    )

    class Meta:
        model = User
        fields = ["email", "full_name", "contact_no"]

        widgets = {
            "email": forms.EmailInput(attrs={"class": "input", "placeholder": "name@example.com"}),
            "full_name": forms.TextInput(attrs={"class": "input", "placeholder": "Your full name"}),
            "contact_no": forms.TextInput(attrs={"class": "input", "placeholder": "10-digit mobile number"}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = "member"  # safest for public signup
        if commit:
            user.save()
        return user

class UserLoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class": "input",
            "placeholder": "Enter email"
        })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "input",
            "placeholder": "Enter password"
        })
    )
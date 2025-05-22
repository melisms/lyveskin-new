from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class UserRegisterForm(UserCreationForm):
    username = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'style': 'width: 200px;'})
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'style': 'width: 200px;'})
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'style': 'width: 200px;'})
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'style': 'width: 200px;'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

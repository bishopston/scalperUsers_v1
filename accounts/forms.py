from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from accounts.models import CustomUser


class UserAdminCreationForm(UserCreationForm):
    """
    A Custom form for creating new users.
    """
    email = forms.EmailField(max_length=254,
                            label="Email address*",
                            widget=forms.EmailInput(
                            attrs={
                            'class': 'form-control form-control-sm',
                            'autocomplete': 'off',
                            'placeholder': 'Email address',
                            }
                            ))

    password1 = forms.CharField(max_length=32,
                            label="Password*",
                            help_text=password_validation.password_validators_help_text_html(),
                            widget=forms.PasswordInput(
                            attrs={
                            'class': 'form-control form-control-sm',
                            'autocomplete': 'new-password',
                            'placeholder': 'Password',
                            }
                            ))

    class Meta:
        model = get_user_model()
        fields = ['email', 'password1']

    def clean_email(self):
        email = self.cleaned_data['email']
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError(
                'Please use another email, this is already taken')
        return email

    def clean(self):
        password_validation.validate_password(self.cleaned_data.get('password1'), None)
        return self.cleaned_data

    def __init__(self, *args, **kwargs):
        super(UserAdminCreationForm, self).__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'autocomplete': 'new-password'})
        del self.fields['password2']

class UserLoginForm(AuthenticationForm):

    email = forms.EmailField(max_length=254, widget=forms.TextInput(
        attrs={'class': 'form-control mb-3', 'placeholder': 'Email', 'id': 'form-email'}))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'id': 'login-pwd',
        }
    ))
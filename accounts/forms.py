from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


class UserAdminCreationForm(UserCreationForm):
    """
    A Custom form for creating new users.
    """
    email = forms.EmailField(max_length=254,
                            label="Email address*",
                            widget=forms.EmailInput(
                            attrs={
                            'class': 'form-control form-control-sm',
                            }
                            ))

    password1 = forms.CharField(max_length=32,
                            label="Password*",
                            help_text=password_validation.password_validators_help_text_html(),
                            widget=forms.PasswordInput(
                            attrs={
                            'class': 'form-control form-control-sm',
                            }
                            ))

    class Meta:
        model = get_user_model()
        fields = ['email', 'password1']

    def clean(self):
        password_validation.validate_password(self.cleaned_data.get('password1'), None)
        return self.cleaned_data

    def __init__(self, *args, **kwargs):
        super(UserAdminCreationForm, self).__init__(*args, **kwargs)
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
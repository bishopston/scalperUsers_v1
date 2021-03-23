from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import ugettext as _

from accounts.models import CustomUser
from option_pricing.models import Optionsymbol

from datetime import datetime, date

EXP_YEAR_CHOICES = [('', 'Select expiration year...'), ('2019', '2019'), ('2020', '2020'), ('2021', '2021'), ('2022', '2022'),]
EXP_MONTH_CHOICES = [
    ('', 'Select expiration month...'),
    ('1', 'JAN'),
    ('2', 'FEB'),
    ('3', 'MAR'),
    ('4', 'APR'),
    ('5', 'MAY'),
    ('6', 'JUN'),
    ('7', 'JUL'),
    ('8', 'AUG'),
    ('9', 'SEP'),
    ('10', 'OCT'),
    ('11', 'NOV'),
    ('12', 'DEC'),
]

ASSETS = [
    ('', 'Select underlying...'),
    ('FTSE', 'FTSE'),
    ('ALPHA', 'ALPHA'),
    ('HTO', 'OTE'),
    ('ETE', 'ETE'),
    ('OPAP', 'OPAP'),
    ('PPC', 'DEH'),
    ('TPEIR', 'PEIRAIOS'),
]

OPTION_TYPE = [
    ('c', 'Call'),
    ('p', 'Put'),
]

POSITION_TYPE = [
    ('Long', 'Long'),
    ('Short', 'Short'),
]

DATES = Optionsymbol.objects.filter(expmonthdate__gte=date.today()).order_by('expmonthdate').values_list('expmonthdate', flat=True).distinct()
DATES_=[]
for i in range(len(DATES)):
    DATES_.append(DATES[i].strftime("%#d-%#m-%Y"))
#_DATES = DATES_.insert(0, float('Select expiration date...'))
#_DATES_ = _DATES[-1:] + _DATES[:-1]

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



class CreatePortfolioForm(forms.Form):
    name = forms.CharField(max_length=30, label='', widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter portfolio name', 'id': 'create-portfolio'}))


class PortfolioOptionForm(forms.Form):

    asset = forms.CharField(
        label='',

        widget=forms.Select(
        choices=ASSETS,

        attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'Select Underlying'
        }
    ))

    option_type = forms.ChoiceField(
        label='',
        widget=forms.RadioSelect(attrs={
        'class': 'form-check-label'
        }),
        choices=OPTION_TYPE,
        initial = 'c'
    )

    exp_month = forms.CharField(
        label='',
        widget=forms.Select(
        choices=EXP_MONTH_CHOICES,
        attrs={
        'class': 'form-control form-control-sm',
        'placeholder': 'Select Expiration Month'
    }
    ))

    exp_year = forms.CharField(
        label='',
        widget=forms.Select(
        choices=EXP_YEAR_CHOICES,
        attrs={
        'class': 'form-control form-control-sm',
        'placeholder': 'Select Expiration Year'
    }
    ))

    strike = forms.DecimalField(
        label='',
        widget=forms.TextInput(
        attrs={
        'class': 'form-control form-control-sm',
        'placeholder': 'Enter Strike'
    }
    ))

    position_type = forms.ChoiceField(
        label='',
        widget=forms.RadioSelect(attrs={
        'class': 'form-check-label'
        }),
        choices=POSITION_TYPE,
        initial = 'Long'
    )

    contracts = forms.IntegerField(
        label='',
        widget=forms.TextInput(
        attrs={
        'class': 'form-control form-control-sm',
        'placeholder': 'Enter Number of Contracts'
    }
    ))

    buysellprice = forms.DecimalField(
        label='',
        widget=forms.TextInput(
        attrs={
        'class': 'form-control form-control-sm',
        'placeholder': 'Enter Buy/Sell price per unit'
    }
    ))
"""
    def clean_strike(self):
        asset_ = self.cleaned_data['asset']
        optiontype_ = self.cleaned_data['option_type']
        expmonth_ = self.cleaned_data['exp_month']
        expyear_ = self.cleaned_data['exp_year']
        strike_ = self.cleaned_data['strike']

        qs = Optionsymbol.objects.filter(asset=asset_).filter(optiontype=optiontype_).filter(expmonthdate__month=expmonth_).filter(expmonthdate__year=expyear_).filter(strike=strike_)
        if qs.exists():                
            return qs
        else:
            raise forms.ValidationError(_("CSV must be a file."))

    def __init__(self, *args, **kwargs):
        super(PortfolioOptionForm, self).__init__(*args, **kwargs)
"""

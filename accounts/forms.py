from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import ugettext as _

from accounts.models import CustomUser
from option_pricing.models import Optionsymbol
from accounts.models import PortfolioOption, PortfolioFuture, PortfolioStock

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

FUTUREASSETS = [
    ('', 'Select underlying...'),
    ('ADMIE', 'ADMIE'),
    ('ALPHA', 'ALPHA'),
    ('BELA', 'JUMBO'),
    ('CENER', 'CENERGY'),
    ('EEE', 'COCA-COLA'),
    ('ELLAK', 'ELLAKTOR'),
    ('ELPE', 'ELPE'),
    ('ETE', 'ETE'),
    ('EUROB', 'EUROBANK'),
    ('EXAE', 'EXAE'),
    ('EYDAP', 'EYDAP'),
    ('FDTR', 'FDTR'),
    ('FOYRK', 'FOURLIS'),
    ('FTSE', 'FTSE'),
    ('GEKTE', 'GEKTERNA'),
    ('HTO', 'OTE'),
    ('INLOT', 'INTRALOT'),
    ('INTRK', 'INTRACOM'),
    ('LAMDA', 'LAMDA'),
    ('MIG', 'MIG'),
    ('MOH', 'MOTOR OIL'),
    ('MYTIL', 'MYTIL'),
    ('OPAP', 'OPAP'),
    ('PPA', 'OLP'),
    ('PPC', 'DEH'),
    ('TATT', 'ATTICA BANK'),
    ('TENER', 'TERNA ENERGY'),
    ('TITC', 'TITAN'),
    ('TPEIR', 'PEIRAIOS'),
    ('VIO', 'VIOHALCO'),
    ]

STOCKASSETS = [
    ('', 'Select stock...'),
    ('ADMIE', 'ADMIE'),
    ('ALPHA', 'ALPHA'),
    ('BELA', 'JUMBO'),
    ('CENER', 'CENERGY'),
    ('EEE', 'COCA-COLA'),
    ('ELLAKTOR', 'ELLAKTOR'),
    ('ELPE', 'ELPE'),
    ('ETE', 'ETE'),
    ('EUROB', 'EUROBANK'),
    ('EXAE', 'EXAE'),
    ('EYDAP', 'EYDAP'),
    ('FOYRK', 'FOURLIS'),
    ('GEKTERNA', 'GEKTERNA'),
    ('HTO', 'OTE'),
    ('INLOT', 'INTRALOT'),
    ('INTRK', 'INTRACOM'),
    ('LAMDA', 'LAMDA'),
    ('MIG', 'MIG'),
    ('MOH', 'MOTOR OIL'),
    ('MYTIL', 'MYTIL'),
    ('OPAP', 'OPAP'),
    ('PPA', 'OLP'),
    ('PPC', 'DEH'),
    ('TATT', 'ATTICA BANK'),
    ('TENERGY', 'TERNA ENERGY'),
    ('TITC', 'TITAN'),
    ('TPEIR', 'PEIRAIOS'),
    ('VIO', 'VIOHALCO'),
    ]

DATES = Optionsymbol.objects.filter(expmonthdate__gte=date.today()).order_by('expmonthdate').values_list('expmonthdate', flat=True).distinct()
""" DATES_=[]
for i in range(len(DATES)):
    DATES_.append(DATES[i].strftime("%#d-%#m-%Y")) """
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
        'placeholder': 'Enter Exercise Price'
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

class PortfolioOptionUpdateForm(forms.Form):

    position_type_upd = forms.ChoiceField(
        label='',
        required=False,
        widget=forms.RadioSelect(attrs={
        'class': 'form-check-label'
        }),
        choices=POSITION_TYPE,
        initial = 'Long'
    )

    contracts_upd = forms.IntegerField(
        label='',
        required=False,
        widget=forms.TextInput(
        attrs={
        'class': 'form-control form-control-sm',
        'placeholder': 'Enter Number of Contracts'
    }
    ))

    buysellprice_upd = forms.DecimalField(
        label='',
        required=False,
        widget=forms.TextInput(
        attrs={
        'class': 'form-control form-control-sm',
        'placeholder': 'Enter Buy/Sell Price per Unit'
    }
    ))

class PortfolioOptionUpdateModelForm(forms.ModelForm):

    class Meta:
        model = PortfolioOption
        fields = ('position', 'contracts', 'buysellprice',)

        widgets = {
            'position':forms.RadioSelect(choices=POSITION_TYPE, attrs={'class': 'form-check-label'}),
            'contracts':forms.TextInput(attrs={
                        'class': 'form-control form-control-sm',
                        'placeholder': 'Enter Number of Contracts'
                        }),
            'buysellprice':forms.TextInput(attrs={
                        'class': 'form-control form-control-sm',
                        'placeholder': 'Enter Buy/Sell price per unit'
                        }),
        }
"""
        def __init__(self, *args, **kwargs):
            super(PortfolioOptionUpdateModelForm, self).__init__(*args, **kwargs)
            self.fields['position'].choices = POSITION_TYPE
"""

class PortfolioFutureForm(forms.Form):

    asset = forms.CharField(
        label='',

        widget=forms.Select(
        choices=FUTUREASSETS,

        attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'Select Underlying'
        }
    ))

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
        'placeholder': 'Enter Buy/Sell Price per Unit'
    }
    ))

class PortfolioFutureUpdateModelForm(forms.ModelForm):

    class Meta:
        model = PortfolioFuture
        fields = ('position', 'contracts', 'buysellprice',)

        widgets = {
            'position':forms.RadioSelect(choices=POSITION_TYPE, attrs={'class': 'form-check-label'}),
            'contracts':forms.TextInput(attrs={
                        'class': 'form-control form-control-sm',
                        'placeholder': 'Enter Number of Contracts'
                        }),
            'buysellprice':forms.TextInput(attrs={
                        'class': 'form-control form-control-sm',
                        'placeholder': 'Enter Buy/Sell price per unit'
                        }),
        }

class PortfolioStockForm(forms.Form):

    asset = forms.CharField(
        label='',
        widget=forms.Select(
        choices=STOCKASSETS,
        attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'Select'
        }
    ))

    quantity = forms.IntegerField(
        label='',
        widget=forms.TextInput(
        attrs={
        'class': 'form-control form-control-sm',
        'placeholder': 'Enter Number of Stocks'
    }
    ))

    buyprice = forms.DecimalField(
        label='',
        widget=forms.TextInput(
        attrs={
        'class': 'form-control form-control-sm',
        'placeholder': 'Enter Buy Price per Stock'
    }
    ))

class PortfolioStockUpdateModelForm(forms.ModelForm):

    class Meta:
        model = PortfolioStock
        fields = ('quantity', 'buyprice',)

        widgets = {
            'quantity':forms.TextInput(attrs={
                        'class': 'form-control form-control-sm',
                        'placeholder': 'Enter Number of Stocks',
                        }),
            'buyprice':forms.TextInput(attrs={
                        'class': 'form-control form-control-sm',
                        'placeholder': 'Enter Buy Price per Stock',
                        }),
        }
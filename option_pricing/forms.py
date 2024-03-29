from django import forms
from . models import Option, Optionsymbol

import datetime

EXP_YEAR_CHOICES = [('', 'Choose...'), ('2019', '2019'), ('2020', '2020'), ('2021', '2021'), ('2022', '2022'),]
EXP_MONTH_CHOICES = [
    ('', 'Choose...'),
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
    ('', 'Choose...'),
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

class OptionScreenerForm(forms.Form):
    asset = forms.CharField(
        label="Underlying Asset",
        widget=forms.Select(
        choices=ASSETS,
        attrs={
            'class': 'form-control form-control-sm',
        }
    ))

    option_type = forms.ChoiceField(
        label='Option Type',
        widget=forms.RadioSelect(attrs={
        'class': 'form-check-label'
        }),
        choices=OPTION_TYPE,
        initial = 'c'

    )

    exp_month = forms.CharField(
        label="Expiration Month",
        widget=forms.Select(
        choices=EXP_MONTH_CHOICES,
        attrs={
        'class': 'form-control form-control-sm'
    }
    ))

    exp_year = forms.CharField(
        label="Expiration Year",
        widget=forms.Select(
        choices=EXP_YEAR_CHOICES,
        attrs={
        'class': 'form-control form-control-sm'
    }
    ))

class FutureScreenerForm(forms.Form):
    exp_month = forms.CharField(
        label="Expiration Month",
        widget=forms.Select(
        choices=EXP_MONTH_CHOICES,
        attrs={
        'class': 'form-control form-control-sm'
    }
    ))

    exp_year = forms.CharField(
        label="Expiration Year",
        widget=forms.Select(
        choices=EXP_YEAR_CHOICES,
        attrs={
        'class': 'form-control form-control-sm'
    }
    ))

class ImpliedperStrikeScreenerForm(forms.Form):
    asset = forms.CharField(
        label="Underlying Asset",
        widget=forms.Select(
        choices=ASSETS,
        attrs={
            'class': 'form-control form-control-sm',
        }
    ))

    option_type = forms.ChoiceField(
        label="Option Type",
        widget=forms.RadioSelect(attrs={
        'class': 'form-check-label'
        }),
        choices=OPTION_TYPE,
        initial = 'c'

    )

    exp_month = forms.CharField(
        label="Expiration Month",
        widget=forms.Select(
        choices=EXP_MONTH_CHOICES,
        attrs={
        'class': 'form-control form-control-sm'
    }
    ))

    exp_year = forms.CharField(
        label="Expiration Year",
        widget=forms.Select(
        choices=EXP_YEAR_CHOICES,
        attrs={
        'class': 'form-control form-control-sm'
    }
    ))

class OptionSearchForm(forms.Form):
    q = forms.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['q'].widget.attrs.update(
            {'class': 'form-control menudd'})
        self.fields['q'].widget.attrs.update(
            {'data-toggle': 'dropdown'})

"""
class OptionSearchForm2(forms.ModelForm):

    class Meta:
        model = Option
        fields = ['optionsymbol']
        widgets = {
            
            'optionsymbol':forms.TextInput(attrs={
                        'class': 'form-control',
                        'placeholder': 'Search option symbol'
                        }),}
 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['optionsymbol'].queryset = Optionsymbol.objects.none() 
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            }) """

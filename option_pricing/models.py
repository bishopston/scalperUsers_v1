from django.db import models
from django.urls import reverse
from accounts.models import CustomUser

class Optionsymbol(models.Model):

    ASSETS = [
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
    symbol = models.CharField(max_length=15)
    asset = models.CharField(max_length=5,
        choices=ASSETS,)
    optiontype = models.CharField(max_length=1, choices=OPTION_TYPE,)
    strike = models.DecimalField(max_digits=8, decimal_places=2)
    expmonthdate = models.DateField()
    favourites = models.ManyToManyField(
	    CustomUser, related_name='favourite', default=None, blank=True)
    optionscreeners = models.ManyToManyField(
	    CustomUser, related_name='optionscreeners', default=None, blank=True)
    likes = models.ManyToManyField(
	    CustomUser, related_name='likes', default=None, blank=True)
    #like_count = models.BigIntegerField(default='0')

    def __str__(self):
        return self.symbol

    def total_likes(self):
        return self.likes.count()

    def get_absolute_url(self):       
        return reverse('option_pricing:option_screener_detail', args=[str(self.symbol)])

class Option(models.Model):

    optionsymbol = models.ForeignKey(Optionsymbol, on_delete=models.CASCADE)
    date = models.DateTimeField()
    closing_price = models.DecimalField(max_digits=8, decimal_places=3)
    change = models.DecimalField(max_digits=10, decimal_places=2)
    volume = models.IntegerField()
    max = models.DecimalField(max_digits=8, decimal_places=3)
    min = models.DecimalField(max_digits=8, decimal_places=3)
    trades = models.IntegerField()
    fixing_price = models.DecimalField(max_digits=8, decimal_places=3)
    open_interest = models.IntegerField()
    stock = models.DecimalField(max_digits=8, decimal_places=2)
    imp_vol = models.DecimalField(max_digits=8, decimal_places=3)
    atm_strike = models.DecimalField(max_digits=8, decimal_places=3)
    frontexpdate = models.DateField()
    expmonth_atm_impvol = models.DecimalField(max_digits=8, decimal_places=3)
    delta = models.DecimalField(max_digits=8, decimal_places=3)
    theta = models.DecimalField(max_digits=8, decimal_places=3)
    gamma = models.DecimalField(max_digits=8, decimal_places=3)
    vega = models.DecimalField(max_digits=8, decimal_places=3)
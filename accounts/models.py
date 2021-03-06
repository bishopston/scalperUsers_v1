from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from option_pricing.models import Optionsymbol, Futuresymbol, Stocksymbol

from datetime import date

POSITION_TYPE = [
        ('Long', 'Long'),
        ('Short', 'Short'),
    ]

class CustomUserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    def _create_user(self, email, password=None, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

class Portfolio(models.Model):
    name = models.CharField(max_length=30)
    creator = models.ForeignKey(
	    settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def active_option_count(self):
        options = PortfolioOption.objects.filter(portfolio=self.id)
        active_options=[]
        for i in range(len(options)):
            if options[i].active_option():
                active_options.append(options[i])
        return len(active_options)

    def active_future_count(self):
        futures = PortfolioFuture.objects.filter(portfolio=self.id)
        active_futures=[]
        for i in range(len(futures)):
            if futures[i].active_future():
                active_futures.append(futures[i])
        return len(active_futures)

    def stock_count(self):
        stocks = PortfolioStock.objects.filter(portfolio=self.id)
        return len(stocks)

class PortfolioOption(models.Model):

    POSITION_TYPE = [
        ('Long', 'Long'),
        ('Short', 'Short'),
    ]

    portfolio = models.ManyToManyField(
	    Portfolio, related_name='optionsportfolio', default=None, blank=True)
    optionsymbol = models.ForeignKey(Optionsymbol, on_delete=models.CASCADE)
    position = models.CharField(max_length=5, choices=POSITION_TYPE, blank=False, default='Long')
    contracts = models.IntegerField()
    buysellprice = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    def active_option(self):
        return self.optionsymbol.expmonthdate >= date.today()

class PortfolioFuture(models.Model):

    portfolio = models.ManyToManyField(Portfolio, related_name='futuresportfolio', default=None, blank=True)
    futuresymbol = models.ForeignKey(Futuresymbol, on_delete=models.CASCADE)
    position = models.CharField(max_length=5, choices=POSITION_TYPE, blank=False, default='Long')
    contracts = models.IntegerField()
    buysellprice = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    def active_future(self):
        return self.futuresymbol.expmonthdate >= date.today()

class PortfolioStock(models.Model):
    portfolio = models.ManyToManyField(
	    Portfolio, related_name='stocksportfolio', default=None, blank=True)
    stocksymbol = models.ForeignKey(Stocksymbol, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    buyprice = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
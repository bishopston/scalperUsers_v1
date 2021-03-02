from django.db import models
from django.urls import reverse
from accounts.models import CustomUser

class Optionseries(models.Model):

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
    asset = models.CharField(max_length=5,
        choices=ASSETS,)
    optiontype = models.CharField(max_length=1, choices=OPTION_TYPE,)
    expmonthdate = models.DateField()
    seriesscreeners = models.ManyToManyField(
	    CustomUser, related_name='seriesscreeners', default=None, blank=True)
    seriesatmscreeners = models.ManyToManyField(
	    CustomUser, related_name='seriesatmscreeners', default=None, blank=True)
    
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
    optionseries = models.ForeignKey(Optionseries, on_delete=models.CASCADE)
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

    @property
    def get_full_name(self):
        return '%s %s %s %s' % (self.asset, self.optiontype, self.expmonthdate__month, self.expmonthdate__year)
    #full_name = property(get_full_name)

    def exp_series(self):
        return self.get_full_name

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

class DailyVolumeCallManager(models.Manager):     
	def get_queryset(self):         
		return super(DailyVolumeCallSumManager, self).get_queryset().filter(optiontype='c')
		
class DailyVolumePutManager(models.Manager):     
	def get_queryset(self):         
		return super(DailyVolumePutSumManager, self).get_queryset().filter(optiontype='p')

class Optionvolume(models.Model):

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
    date = models.DateField()
    asset = models.CharField(max_length=5,
        choices=ASSETS,)
    optiontype = models.CharField(max_length=1, choices=OPTION_TYPE,)
    expmonthdate = models.DateField()
    volume = models.IntegerField()
    trades = models.IntegerField()
    open_interest = models.IntegerField()

    objects = models.Manager()  # The default manager. 
    dailyVolumeCall = DailyVolumeCallManager()
    dailyVolumePut = DailyVolumePutManager()

class Optionvolumeaggseries(models.Model):

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
    date = models.DateField()
    asset = models.CharField(max_length=5,
        choices=ASSETS,)
    optiontype = models.CharField(max_length=1, choices=OPTION_TYPE,)
    volume = models.IntegerField()
    trades = models.IntegerField()
    open_interest = models.IntegerField()

class Optionvolumeaggseriesasset(models.Model):

    OPTION_TYPE = [
        ('c', 'Call'),
        ('p', 'Put'),
    ]
    date = models.DateField()
    optiontype = models.CharField(max_length=1, choices=OPTION_TYPE,)
    volume = models.IntegerField()
    trades = models.IntegerField()
    open_interest = models.IntegerField()

class Optioncallputmonthlyratio(models.Model):

    date = models.DateField()
    sum_vol_calls = models.IntegerField()
    sum_vol_puts = models.IntegerField()
    callputratio = models.DecimalField(max_digits=8, decimal_places=3)

class Futuresymbol(models.Model):

    FUTUREASSETS = [
    ('ADMIE', 'ADMIE'),
    ('ALPHA', 'ALPHA'),
    ('BELA', 'JUMBO'),
    ('CENER', 'CENERGY'),
    ('EEE', 'COCA-COLA'),
    ('ELLAK', 'ELLAKTOR'),
    ('ELPE', 'ELPE'),
    ('ETE', 'ETE'),
    ('EUROB', 'EUROB'),
    ('EXAE', 'EXAE'),
    ('EYDAP', 'EYDAP'),
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

    symbol = models.CharField(max_length=15)
    asset = models.CharField(max_length=5,
        choices=FUTUREASSETS,)
    expmonthdate = models.DateField()
    favourites = models.ManyToManyField(
	    CustomUser, related_name='favourite_future', default=None, blank=True)
    futurescreeners = models.ManyToManyField(
	    CustomUser, related_name='futurescreeners', default=None, blank=True)

    def __str__(self):
        return self.symbol

    def get_absolute_url(self):       
        return reverse('option_pricing:future_screener_detail', args=[str(self.symbol)])

class Future(models.Model):

    futuresymbol = models.ForeignKey(Futuresymbol, on_delete=models.CASCADE)
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

class Stocksymbol(models.Model):

    ASSETS = [
    ('ADMIE', 'ADMIE'),
    ('ALPHA', 'ALPHA'),
    ('BELA', 'JUMBO'),
    ('CENER', 'CENERGY'),
    ('GD', 'GD'),
    ('EEE', 'COCA-COLA'),
    ('ELLAKTOR', 'ELLAKTOR'),
    ('ELPE', 'ELPE'),
    ('ETE', 'ETE'),
    ('EUROB', 'EUROB'),
    ('EXAE', 'EXAE'),
    ('EYDAP', 'EYDAP'),
    ('FOYRK', 'FOURLIS'),
    ('FTSE', 'FTSE'),
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

    symbol = models.CharField(max_length=15)
    asset = models.CharField(max_length=10,
        choices=ASSETS,)

    def __str__(self):
	    return self.symbol

class Stock(models.Model):
    stocksymbol = models.ForeignKey(Stocksymbol, on_delete=models.CASCADE, default=0)
    date = models.DateTimeField()
    high = models.DecimalField(max_digits=8, decimal_places=3)
    low = models.DecimalField(max_digits=8, decimal_places=3)
    open = models.DecimalField(max_digits=8, decimal_places=3)
    close = models.DecimalField(max_digits=8, decimal_places=3)
    volume = models.FloatField()
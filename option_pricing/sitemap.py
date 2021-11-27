from django.contrib.sitemaps import Sitemap
from .models import Optionsymbol, Futuresymbol, Stocksymbol

class OptionsymbolSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.9
    def items(self):
        return Optionsymbol.objects.all().order_by('-expmonthdate')

class FuturesymbolSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.9
    def items(self):
        return Futuresymbol.objects.all().order_by('-expmonthdate')

class StocksymbolSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.9
    def items(self):
        return Stocksymbol.objects.all().order_by('-symbol')
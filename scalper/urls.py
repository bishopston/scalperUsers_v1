from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.sitemaps.views import sitemap
from option_pricing.sitemap import OptionsymbolSitemap, FuturesymbolSitemap, StocksymbolSitemap

sitemaps={
    'optionsymbol':OptionsymbolSitemap,
    'futuresymbol':FuturesymbolSitemap,
    'stocksymbol':StocksymbolSitemap
}


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('option_pricing.urls', namespace='option_pricing')),
    path(
        'sitemap.xml',sitemap, {'sitemaps':sitemaps}, name='django.contrib.sitemaps.views.sitemap'
    )
]

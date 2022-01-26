from django.urls import path
from .views import OptionSymbol, OptionHistData, OptionSymbolAsset

urlpatterns = [
    path('optionsymbol/', OptionSymbol.as_view()),
    path('optionsymbolasset/', OptionSymbolAsset.as_view()),
    # path('optionsymboldata/<str:optionsymbol>/', OptionHistData.as_view()),
    path('optionsymboldata/', OptionHistData.as_view()),
]
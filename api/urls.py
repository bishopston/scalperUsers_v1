from django.urls import path
from .views import OptionSymbol, OptionHistData, OptionSymbolAsset, FutureSymbol, FutureHistData, FutureSymbolAsset

urlpatterns = [
    path('optionsymbol/', OptionSymbol.as_view()),
    path('optionsymbolasset/', OptionSymbolAsset.as_view()),
    # path('optionsymboldata/<str:optionsymbol>/', OptionHistData.as_view()),
    path('optionsymboldata/', OptionHistData.as_view()),
    path('futuresymbol/', FutureSymbol.as_view()),
    path('futuresymboldata/', FutureHistData.as_view()),
    path('futuresymbolasset/', FutureSymbolAsset.as_view()),
]
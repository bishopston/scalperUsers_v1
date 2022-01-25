from django.urls import path
from .views import OptionSymbolHist, OptionHist

urlpatterns = [
    path('optionsymbol/', OptionSymbolHist.as_view()),
    path('optionsymbol/<str:optionsymbol>/', OptionHist.as_view()),
]
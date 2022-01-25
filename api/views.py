
from rest_framework import generics
from option_pricing.models import Option, Optionsymbol
from .serializers import OptionSerializer, OptionSymbolSerializer


class OptionSymbolHist(generics.ListAPIView):
    serializer_class = OptionSymbolSerializer

    def get_queryset(self):
        queryset = Optionsymbol.objects.all().order_by('-expmonthdate')
        optionsymbol = self.request.query_params.get('symbol')
        if optionsymbol is not None:
            queryset = queryset.filter(symbol=optionsymbol)
        return queryset


class OptionHist(generics.ListAPIView):
    serializer_class = OptionSerializer

    def get_queryset(self):
        optionsymbol = self.kwargs['optionsymbol']
        qs = Option.objects.filter(optionsymbol__symbol=optionsymbol)
        return qs.order_by('-date')
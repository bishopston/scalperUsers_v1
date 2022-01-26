from rest_framework import generics
from option_pricing.models import Option, Optionsymbol
from .serializers import OptionSerializer, OptionSymbolSerializer, OptionAssetSerializer


class OptionSymbol(generics.ListAPIView):
    serializer_class = OptionSymbolSerializer

    def get_queryset(self):
        queryset = Optionsymbol.objects.all().order_by('-expmonthdate')
        optionsymbol = self.request.query_params.get('symbol')
        if optionsymbol is not None:
            queryset = queryset.filter(symbol=optionsymbol)
        return queryset

class OptionSymbolAsset(generics.ListAPIView):
    serializer_class = OptionSymbolSerializer

    def get_queryset(self):
        queryset = Optionsymbol.objects.all().order_by('-expmonthdate')
        asset = self.request.query_params.get('asset')
        optiontype = self.request.query_params.get('optiontype')
        expmonthdate = self.request.query_params.get('expmonthdate')
        if None not in (asset, optiontype, expmonthdate):
            queryset = queryset.filter(asset=asset, optiontype=optiontype, expmonthdate=expmonthdate)
            return queryset
        else:
            queryset = Optionsymbol.objects.none()
            return queryset


""" class OptionHistData(generics.ListAPIView):
    serializer_class = OptionSerializer

    def get_queryset(self):
        optionsymbol = self.kwargs['optionsymbol']
        qs = Option.objects.filter(optionsymbol__symbol=optionsymbol)
        return qs.order_by('-date') """

class OptionHistData(generics.ListAPIView):
    serializer_class = OptionSerializer

    def get_queryset(self):
        queryset = Option.objects.all().order_by('date')
        optionsymbol = self.request.query_params.get('symbol')
        if optionsymbol is not None:
            queryset = queryset.filter(optionsymbol__symbol=optionsymbol)
            return queryset
        else:
            queryset = Option.objects.none()
            return queryset
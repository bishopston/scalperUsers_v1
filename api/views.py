from rest_framework import generics
from option_pricing.models import Option, Optionsymbol, Future, Futuresymbol
from .serializers import OptionSerializer, OptionSymbolSerializer, FutureSerializer, FutureSymbolSerializer


class OptionSymbol(generics.ListAPIView):
    serializer_class = OptionSymbolSerializer

    def get_queryset(self):
        queryset = Optionsymbol.objects.all().order_by('expmonthdate')
        optionsymbol = self.request.query_params.get('symbol')
        if optionsymbol is not None:
            queryset = queryset.filter(symbol=optionsymbol)
            return queryset
        else:
            queryset = Optionsymbol.objects.none()
            return queryset

class OptionSymbolAsset(generics.ListAPIView):
    serializer_class = OptionSymbolSerializer

    def get_queryset(self):
        queryset = Optionsymbol.objects.all().order_by('asset', 'optiontype', 'expmonthdate', 'strike')
        asset = self.request.query_params.get('asset')
        optiontype = self.request.query_params.get('optiontype')
        expmonthdate = self.request.query_params.get('expmonthdate')
        if None not in (asset, optiontype, expmonthdate):
            queryset = queryset.filter(asset=asset, optiontype=optiontype, expmonthdate=expmonthdate).order_by('strike')
            return queryset
        elif expmonthdate is None and None not in (asset, optiontype):
            queryset = queryset.filter(asset=asset, optiontype=optiontype).order_by('expmonthdate', 'strike')
            return queryset
        elif optiontype is None and None not in (asset, expmonthdate):
            queryset = queryset.filter(asset=asset, expmonthdate=expmonthdate).order_by('optiontype', 'strike')
            return queryset
        elif asset is None and None not in (optiontype, expmonthdate):
            queryset = queryset.filter(optiontype=optiontype, expmonthdate=expmonthdate).order_by('asset', 'strike')
            return queryset
        elif asset != None and None in (optiontype, expmonthdate):
            queryset = queryset.filter(asset=asset).order_by('expmonthdate', 'optiontype', 'strike')
            return queryset
        elif optiontype != None and None in (asset, expmonthdate):
            queryset = queryset.filter(optiontype=optiontype).order_by('asset', 'expmonthdate', 'strike')
            return queryset
        elif expmonthdate != None and None in (asset, optiontype):
            queryset = queryset.filter(expmonthdate=expmonthdate).order_by('asset', 'optiontype', 'strike')
            return queryset
        else:
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

class FutureSymbol(generics.ListAPIView):
    serializer_class = FutureSymbolSerializer

    def get_queryset(self):
        queryset = Futuresymbol.objects.all().order_by('expmonthdate')
        futuresymbol = self.request.query_params.get('symbol')
        if futuresymbol is not None:
            queryset = queryset.filter(symbol=futuresymbol)
            return queryset
        else:
            queryset = Futuresymbol.objects.none()
            return queryset

class FutureHistData(generics.ListAPIView):
    serializer_class = FutureSerializer

    def get_queryset(self):
        queryset = Future.objects.all().order_by('date')
        futuresymbol = self.request.query_params.get('symbol')
        if futuresymbol is not None:
            queryset = queryset.filter(futuresymbol__symbol=futuresymbol)
            return queryset
        else:
            queryset = Future.objects.none()
            return queryset

class FutureSymbolAsset(generics.ListAPIView):
    serializer_class = FutureSymbolSerializer

    def get_queryset(self):
        queryset = Futuresymbol.objects.all().order_by('asset', 'expmonthdate')
        asset = self.request.query_params.get('asset')
        expmonthdate = self.request.query_params.get('expmonthdate')
        if None not in (asset, expmonthdate):
            queryset = queryset.filter(asset=asset, expmonthdate=expmonthdate).order_by('expmonthdate')
            return queryset
        elif expmonthdate is None and asset != None:
            queryset = queryset.filter(asset=asset).order_by('expmonthdate')
            return queryset
        elif asset is None and expmonthdate != None:
            queryset = queryset.filter(expmonthdate=expmonthdate).order_by('asset')
            return queryset
        else:
            return queryset
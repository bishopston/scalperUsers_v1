from django.shortcuts import render, redirect
from django.db.models import Max, Min, Avg, Sum, F
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.views.generic import View
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.views.generic.base import TemplateView
from django.core import serializers

from datetime import datetime, date
import calendar
import json
from decimal import Decimal
from itertools import chain

from .models import Option, Optioncsv, Optionsymbol, Optionseries, Optionvolume, Optionvolumeaggseries, Optionvolumeaggseriesasset, Optioncallputmonthlyratio, Future, Futurecsv, Futuresymbol, Futurevolumeaggasset, Stocksymbol
from accounts.models import CustomUser
from .forms import OptionScreenerForm, FutureScreenerForm, ImpliedperStrikeScreenerForm, OptionSearchForm

import csv

def home(request):
    form = OptionSearchForm()
    return render(request, 'option_pricing/index.html', {'form': form})
"""
def OptionView(request):
    option = Option.objects.all()
    
    asset_query = request.GET.get('asset')
    callputflag_query = request.GET.get('option_type')
    exp_month_query = request.GET.get('exp_month')
    exp_year_query = request.GET.get('exp_year')

    if asset_query != '' and asset_query is not None:
        option = option.filter(optionsymbol__asset__iexact=asset_query)

    if callputflag_query != '' and callputflag_query is not None:
        option = option.filter(optionsymbol__optiontype__iexact=callputflag_query)

    if exp_month_query != '' and exp_month_query is not None:
        option = option.filter(optionsymbol__expmonthdate__month=exp_month_query)

    if exp_year_query != '' and exp_year_query is not None:
        option = option.filter(optionsymbol__expmonthdate__year=exp_year_query)

    max_date = option.aggregate(Max('date'))
    queryset = option.filter(date=max_date['date__max']).order_by('optionsymbol__strike')

    queryset_num = queryset.count()

    paginator = Paginator(queryset, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'queryset' : queryset,
        'max_date' : max_date,
        'asset_query': asset_query,
        'callputflag_query': callputflag_query,
        'exp_month_query' : exp_month_query,
        'exp_year_query' : exp_year_query,
        'optionscreenerform' : OptionScreenerForm(),
        'queryset_num' : queryset_num,
        'page_obj': page_obj
    }
    return render(request, 'option_pricing/option.html', context)
"""
def OptionScreenerDetail(request, optionsymbol):
    option_strikespan = Option.objects.filter(optionsymbol__symbol=optionsymbol).order_by('-date')
    trade_symbol = optionsymbol
    option_count = option_strikespan.count()
    closing_price = option_strikespan[0].closing_price
    change = option_strikespan[0].change
    asset = option_strikespan[0].optionsymbol.get_asset_display()
    optiontype = option_strikespan[0].optionsymbol.get_optiontype_display()
    """
    if optiontype == 'c': 
        optiontype = 'Call'
    else:
        optiontype = 'Put'
    """
    expmonth = option_strikespan[0].optionsymbol.expmonthdate.strftime("%B")
    expyear = option_strikespan[0].optionsymbol.expmonthdate.strftime("%Y")
    expdate = option_strikespan[0].optionsymbol.expmonthdate.strftime("%#d-%#m-%Y")
    strike = option_strikespan[0].optionsymbol.strike
    latest_trad_date = option_strikespan[0].date.strftime("%#d-%#m-%Y")
    volume = option_strikespan[0].volume
    trades = option_strikespan[0].trades
    open_interest = option_strikespan[0].open_interest
    imp_vol = "{:.2%}".format(option_strikespan[0].imp_vol)
    stock = option_strikespan[0].stock
    moneyness = 'moneyness'

    if optiontype == 'Call' and stock > strike: 
        moneyness = 'ITM'
    elif optiontype == 'Call' and stock < strike:
        moneyness = 'OTM'
    elif optiontype == 'Put' and stock > strike: 
        moneyness = 'OTM'
    elif optiontype == 'Put' and stock < strike:
        moneyness = 'ITM'
    else:
        moneyness = 'ATM'

    lifetime_high = option_strikespan.aggregate(Max('closing_price'))
    lifetime_low = option_strikespan.aggregate(Min('closing_price'))
    delta = option_strikespan[0].delta
    gamma = option_strikespan[0].gamma
    theta = option_strikespan[0].theta
    vega = option_strikespan[0].vega

    is_fav = False
    if option_strikespan[0].optionsymbol.optionscreeners.filter(id=request.user.id).exists():
        is_fav = True

    optionsymbol_id = option_strikespan[0].optionsymbol_id
  
    is_liked = False
    if option_strikespan[0].optionsymbol.likes.filter(id=request.user.id).exists():
        is_liked = True

    context = {
        'option_strikespan' : option_strikespan,
        'trade_symbol' : trade_symbol,
        'option_count' : option_count,
        'closing_price' : round(closing_price,3),
        'change' : change,
        'asset' : asset,
        'optiontype' : optiontype,
        'expmonth' : expmonth,
        'expyear' : expyear,
        'expdate' : expdate,
        'strike' : strike,
        'latest_trad_date' : latest_trad_date,
        'volume' : volume,
        'trades' : trades,
        'open_interest' : open_interest,
        'imp_vol' : imp_vol,
        'moneyness' : moneyness,
        'lifetime_high' : lifetime_high['closing_price__max'],
        'lifetime_low' : lifetime_low['closing_price__min'],
        'delta' : delta,
        'theta' : theta,
        'gamma' : gamma,
        'vega' : vega,
        'is_fav' : is_fav,
        'is_liked': is_liked,
        'optionsymbol_id' : optionsymbol_id,
        'total_likes' : option_strikespan[0].optionsymbol.total_likes(),
        #'optionsymbol_like_count' :optionsymbol_like_count,
    }

    return render(request, 'option_pricing/option_screener.html', context)

def OptionJSChartView(request, tradesymbol):
    optiondata = []

    option = Option.objects.filter(optionsymbol__symbol=tradesymbol).order_by('date')

    for i in option:
        optiondata.append({json.dumps(i.date.strftime("%#d-%#m-%Y")):i.closing_price})

    #print(optiondata)
    return JsonResponse(optiondata, safe=False)

def OptionJSChartVolView(request, tradesymbol):
    voldata = []

    vol = Option.objects.filter(optionsymbol__symbol=tradesymbol).order_by('date')

    for i in vol:
        voldata.append({json.dumps(i.date.strftime("%#d-%#m-%Y")):i.volume})
    
    #print(voldata)
    return JsonResponse(voldata, safe=False)

def OptionJSDeltaChartView(request, tradesymbol):
    deltadata = []

    option_delta = Option.objects.filter(optionsymbol__symbol=tradesymbol).order_by('date')

    for i in option_delta:
        deltadata.append({json.dumps(i.date.strftime("%#d-%#m-%Y")):i.delta})

    #print(optiondata)
    return JsonResponse(deltadata, safe=False)

def OptionJSGammaChartView(request, tradesymbol):
    gammadata = []

    option_gamma = Option.objects.filter(optionsymbol__symbol=tradesymbol).order_by('date')

    for i in option_gamma:
        gammadata.append({json.dumps(i.date.strftime("%#d-%#m-%Y")):i.gamma})

    #print(optiondata)
    return JsonResponse(gammadata, safe=False)

def OptionJSThetaChartView(request, tradesymbol):
    thetadata = []

    option_theta = Option.objects.filter(optionsymbol__symbol=tradesymbol).order_by('date')

    for i in option_theta:
        thetadata.append({json.dumps(i.date.strftime("%#d-%#m-%Y")):i.theta})

    #print(optiondata)
    return JsonResponse(thetadata, safe=False)

def OptionJSVegaChartView(request, tradesymbol):
    vegadata = []

    option_vega = Option.objects.filter(optionsymbol__symbol=tradesymbol).order_by('date')

    for i in option_vega:
        vegadata.append({json.dumps(i.date.strftime("%#d-%#m-%Y")):i.vega})

    #print(optiondata)
    return JsonResponse(vegadata, safe=False)

def OptionJSImpliedChartView(request, tradesymbol):
    implieddata = []

    option_implied = Option.objects.filter(optionsymbol__symbol=tradesymbol).order_by('date')

    for i in option_implied:
        implieddata.append({json.dumps(i.date.strftime("%#d-%#m-%Y")):i.imp_vol})

    #print(optiondata)
    return JsonResponse(implieddata, safe=False)

def FutureView(request):
    future = Future.objects.all()
    
    exp_month_query = request.GET.get('exp_month')
    exp_year_query = request.GET.get('exp_year')

    if exp_month_query != '' and exp_month_query is not None:
        future = future.filter(futuresymbol__expmonthdate__month=exp_month_query)

    if exp_year_query != '' and exp_year_query is not None:
        future = future.filter(futuresymbol__expmonthdate__year=exp_year_query)

    max_date = future.aggregate(Max('date'))
    queryset = future.filter(date=max_date['date__max']).order_by('futuresymbol__asset')

    queryset_num = queryset.count()

    paginator = Paginator(queryset, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'queryset' : queryset,
        'max_date' : max_date,
        'exp_month_query' : exp_month_query,
        'exp_year_query' : exp_year_query,
        'futurescreenerform' : FutureScreenerForm(),
        'queryset_num' : queryset_num,
        'page_obj': page_obj
    }
    return render(request, 'option_pricing/future.html', context)

def FutureScreenerDetail(request, futuresymbol):
    future_strikespan = Future.objects.filter(futuresymbol__symbol=futuresymbol).order_by('-date')
    trade_symbol = futuresymbol
    future_count = future_strikespan.count()
    closing_price = future_strikespan[0].closing_price
    change = future_strikespan[0].change
    asset = future_strikespan[0].futuresymbol.get_asset_display()

    expmonth = future_strikespan[0].futuresymbol.expmonthdate.strftime("%B")
    expyear = future_strikespan[0].futuresymbol.expmonthdate.strftime("%Y")
    expdate = future_strikespan[0].futuresymbol.expmonthdate.strftime("%#d-%#m-%Y")

    latest_trad_date = future_strikespan[0].date.strftime("%#d-%#m-%Y")
    volume = future_strikespan[0].volume
    trades = future_strikespan[0].trades
    open_interest = future_strikespan[0].open_interest

    stock = future_strikespan[0].stock 
    basis = stock - closing_price
 
    max = future_strikespan[0].max
    min = future_strikespan[0].min
    lifetime_high = future_strikespan.aggregate(Max('closing_price'))
    lifetime_low = future_strikespan.aggregate(Min('closing_price'))

    is_fav = False
    if future_strikespan[0].futuresymbol.futurescreeners.filter(id=request.user.id).exists():
        is_fav = True

    futuresymbol_id = future_strikespan[0].futuresymbol_id
  
    context = {
        'future_strikespan' : future_strikespan,
        'trade_symbol' : trade_symbol,
        'future_count' : future_count,
        'closing_price' : round(closing_price,3),
        'change' : change,
        'asset' : asset,
        'expmonth' : expmonth,
        'expyear' : expyear,
        'expdate' : expdate,
        'latest_trad_date' : latest_trad_date,
        'volume' : volume,
        'trades' : trades,
        'open_interest' : open_interest,
        'stock' : stock,
        'basis' : basis,
        'max' : max,
        'min' : min,
        'lifetime_high' : lifetime_high['closing_price__max'],
        'lifetime_low' : lifetime_low['closing_price__min'],
        'is_fav' : is_fav,
        'futuresymbol_id' : futuresymbol_id,
        #'total_likes' : option_strikespan[0].optionsymbol.total_likes(),
        #'optionsymbol_like_count' :optionsymbol_like_count,
    }
    #print(trade_symbol)
    return render(request, 'option_pricing/future_screener.html', context)

def FutureJSChartView(request, tradesymbol):
    futuredata = []

    future = Future.objects.filter(futuresymbol__symbol=tradesymbol).order_by('date')

    for i in future:
        futuredata.append({json.dumps(i.date.strftime("%#d-%#m-%Y")):i.closing_price})

    #print(optiondata)
    return JsonResponse(futuredata, safe=False)

def FutureJSChartVolView(request, tradesymbol):
    voldata = []

    vol = Future.objects.filter(futuresymbol__symbol=tradesymbol).order_by('date')

    for i in vol:
        voldata.append({json.dumps(i.date.strftime("%#d-%#m-%Y")):i.volume})
    
    #print(voldata)
    return JsonResponse(voldata, safe=False)

def FutureJSSportChartView(request, tradesymbol):
    futurespotdata = []

    futurespot = Future.objects.filter(futuresymbol__symbol=tradesymbol).order_by('date')

    for i in futurespot:
        futurespotdata.append({json.dumps(i.date.strftime("%#d-%#m-%Y")):i.stock})

    #print(optiondata)
    return JsonResponse(futurespotdata, safe=False)


class OptionScreenersListCBV(View):
    def get(self, request):
        option = Option.objects.all()
        
        asset_query = request.GET.get('asset')
        callputflag_query = request.GET.get('option_type')
        exp_month_query = request.GET.get('exp_month')
        exp_year_query = request.GET.get('exp_year')

        if asset_query != '' and asset_query is not None:
            option = option.filter(optionsymbol__asset__iexact=asset_query)

        if callputflag_query != '' and callputflag_query is not None:
            option = option.filter(optionsymbol__optiontype__iexact=callputflag_query)

        if exp_month_query != '' and exp_month_query is not None:
            option = option.filter(optionsymbol__expmonthdate__month=exp_month_query)

        if exp_year_query != '' and exp_year_query is not None:
            option = option.filter(optionsymbol__expmonthdate__year=exp_year_query)

        max_date = option.aggregate(Max('date'))
        queryset = option.filter(date=max_date['date__max']).order_by('optionsymbol__strike')

        queryset_num = queryset.count()

        paginator = Paginator(queryset, 10)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        context = {
            'queryset' : queryset,
            'max_date' : max_date,
            'asset_query': asset_query,
            'callputflag_query': callputflag_query,
            'exp_month_query' : exp_month_query,
            'exp_year_query' : exp_year_query,
            'optionscreenerform' : OptionScreenerForm(),
            'queryset_num' : queryset_num,
            'page_obj': page_obj
        }
        return render(request, 'option_pricing/optionfavlist.html', context)
    
    def post(self, request, *args, **kwargs):
        if request.method == "POST":
            option_ids = request.POST.getlist('id[]')
            is_fav = False
            for id in option_ids:
                opt = Option.objects.get(pk=id)
                if opt.optionsymbol.optionscreeners.filter(id=request.user.id).exists():
                    #opt.optionsymbol.optionscreeners.remove(request.user)
                    is_fav = False
                else:
                    opt.optionsymbol.optionscreeners.add(request.user)
                    is_fav = True
            return redirect('option_pricing:myoptionscreenerlistcbv')

def OptionScreenersDataView(request):
    option = Option.objects.all()
    
    asset_query = request.GET.get('asset')
    callputflag_query = request.GET.get('option_type')
    exp_month_query = request.GET.get('exp_month')
    exp_year_query = request.GET.get('exp_year')

    if asset_query != '' and asset_query is not None:
        option = option.filter(optionsymbol__asset__iexact=asset_query)

    if callputflag_query != '' and callputflag_query is not None:
        option = option.filter(optionsymbol__optiontype__iexact=callputflag_query)

    if exp_month_query != '' and exp_month_query is not None:
        option = option.filter(optionsymbol__expmonthdate__month=exp_month_query)

    if exp_year_query != '' and exp_year_query is not None:
        option = option.filter(optionsymbol__expmonthdate__year=exp_year_query)

    max_date = option.aggregate(Max('date'))
    queryset = option.filter(date=max_date['date__max']).order_by('optionsymbol__strike')

    queryset_num = queryset.count()

    paginator = Paginator(queryset, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
    'queryset' : queryset,
    'max_date' : max_date,
    'asset_query': asset_query,
    'callputflag_query': callputflag_query,
    'exp_month_query' : exp_month_query,
    'exp_year_query' : exp_year_query,
    'queryset_num' : queryset_num,
    'page_obj': page_obj
    }

    if request.is_ajax():
        html = render_to_string('option_pricing/option_screeners_data.html', context, request=request)
    
    return JsonResponse({'form' : html})


def OptionGreatestOI(request):
    return render(request, "option_pricing/optionsgreatestOI.html")

def OptionGreatestOIFetch(request):
    limit=request.GET.get('limit')
    start=request.GET.get('start')
    max_date = Option.objects.all().aggregate(Max('date'))
    qs = Option.objects.all().filter(date=max_date['date__max']).filter(optionsymbol__expmonthdate__gte=max_date['date__max']).order_by('-open_interest')[:30][int(start):int(start) + int(limit)]
    #optionsOI = options[int(start):int(start) + int(limit)]
    context={
        'qs':qs
    }
    return render(request, 'option_pricing/optionsgreatestOI_fetch.html', context)
"""
def OptionDescendingOI(request):
    max_date = Option.objects.all().aggregate(Max('date'))
    queryset = Option.objects.all().filter(date=max_date['date__max']).filter(optionsymbol__expmonthdate__gte=max_date['date__max']).order_by('-open_interest')[:30]
    paginator = Paginator(queryset, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    context={
        'queryset':queryset,
        'page_obj':page_obj
    }
    return render(request, 'option_pricing/option_descendingOI.html', context)
"""

class OptionDescendingOI(View):
    def get(self, request):
        max_date = Option.objects.all().aggregate(Max('date'))
        queryset = Option.objects.all().filter(date=max_date['date__max']).filter(optionsymbol__expmonthdate__gte=max_date['date__max']).order_by('-open_interest')[:30]

        paginator = Paginator(queryset, 10)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        context = {
            'queryset' : queryset,
            'page_obj': page_obj
        }
        return render(request, 'option_pricing/option_descendingOI.html', context)
    
    def post(self, request, *args, **kwargs):
        if request.method == "POST":
            option_ids = request.POST.getlist('id[]')
            is_fav = False
            for id in option_ids:
                opt = Option.objects.get(pk=id)
                if opt.optionsymbol.optionscreeners.filter(id=request.user.id).exists():
                    #opt.optionsymbol.optionscreeners.remove(request.user)
                    is_fav = False
                else:
                    opt.optionsymbol.optionscreeners.add(request.user)
                    is_fav = True
            return redirect('option_pricing:option_descendingOI')


class FutureDescendingOI(View):
    def get(self, request):
        max_date = Future.objects.all().aggregate(Max('date'))
        queryset = Future.objects.all().filter(date=max_date['date__max']).filter(futuresymbol__expmonthdate__gte=max_date['date__max']).order_by('-open_interest')[:30]

        paginator = Paginator(queryset, 10)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        context = {
            'queryset' : queryset,
            'page_obj': page_obj
        }
        return render(request, 'option_pricing/future_descendingOI.html', context)
    
    def post(self, request, *args, **kwargs):
        if request.method == "POST":
            future_ids = request.POST.getlist('id[]')
            is_fav = False
            for id in future_ids:
                item = Future.objects.get(pk=id)
                if item.futuresymbol.futurescreeners.filter(id=request.user.id).exists():
                    #opt.optionsymbol.optionscreeners.remove(request.user)
                    is_fav = False
                else:
                    item.futuresymbol.futurescreeners.add(request.user)
                    is_fav = True
            return redirect('option_pricing:future_descendingOI')


class FutureScreenersListCBV(View):
    def get(self, request):
        future = Future.objects.all()
        
        exp_month_query = request.GET.get('exp_month')
        exp_year_query = request.GET.get('exp_year')

        if exp_month_query != '' and exp_month_query is not None:
            future = future.filter(futuresymbol__expmonthdate__month=exp_month_query)

        if exp_year_query != '' and exp_year_query is not None:
            future = future.filter(futuresymbol__expmonthdate__year=exp_year_query)

        max_date = future.aggregate(Max('date'))
        queryset = future.filter(date=max_date['date__max']).order_by('futuresymbol__asset')

        queryset_num = queryset.count()

        paginator = Paginator(queryset, 10)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        context = {
            'queryset' : queryset,
            'max_date' : max_date,
            'exp_month_query' : exp_month_query,
            'exp_year_query' : exp_year_query,
            'futurescreenerform' : FutureScreenerForm(),
            'queryset_num' : queryset_num,
            'page_obj': page_obj
        }
        return render(request, 'option_pricing/futurefavlist.html', context)
    
    def post(self, request, *args, **kwargs):
        if request.method == "POST":
            future_ids = request.POST.getlist('id[]')
            is_fav = False
            for id in future_ids:
                item = Future.objects.get(pk=id)
                if item.futuresymbol.futurescreeners.filter(id=request.user.id).exists():
                    #opt.optionsymbol.optionscreeners.remove(request.user)
                    is_fav = False
                else:
                    item.futuresymbol.futurescreeners.add(request.user)
                    is_fav = True
            return redirect('option_pricing:myfuturescreenerlistcbv')
"""
def ImpliedperStrikeScreenerView(request):
    option = Option.objects.all()
    
    asset_query = request.GET.get('asset')
    callputflag_query = request.GET.get('option_type')
    exp_month_query = request.GET.get('exp_month')
    exp_year_query = request.GET.get('exp_year')

    if asset_query != '' and asset_query is not None:
        option = option.filter(optionsymbol__asset__iexact=asset_query)

    if callputflag_query != '' and callputflag_query is not None:
        option = option.filter(optionsymbol__optiontype__iexact=callputflag_query)

    if exp_month_query != '' and exp_month_query is not None:
        option = option.filter(optionsymbol__expmonthdate__month=exp_month_query)

    if exp_year_query != '' and exp_year_query is not None:
        option = option.filter(optionsymbol__expmonthdate__year=exp_year_query)

    max_date = option.aggregate(Max('date'))
    queryset = option.filter(date=max_date['date__max']).order_by('optionsymbol__strike')

    queryset_num = queryset.count()

    context = {
        'queryset' : queryset,
        'max_date' : max_date,
        'asset_query': asset_query,
        'callputflag_query': callputflag_query,
        'exp_month_query' : exp_month_query,
        'exp_year_query' : exp_year_query,
        'ivperstrikescreenerform' : ImpliedperStrikeScreenerForm(),
        'queryset_num' : queryset_num,
    }
    return render(request, 'option_pricing/ivperstrike.html', context)
"""
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return json.JSONEncoder.default(self, obj)

def IVscreenerChartView(request, asset, optiontype, expmonth, expyear):
    ivdata = []

    screener = Option.objects.filter(optionsymbol__optionseries__asset=asset).filter(optionsymbol__optionseries__optiontype=optiontype).filter(optionsymbol__optionseries__expmonthdate__month=expmonth).filter(optionsymbol__optionseries__expmonthdate__year=expyear)
    max_date = screener.aggregate(Max('date'))
    queryset = screener.filter(date=max_date['date__max']).order_by('optionsymbol__strike')

    for i in queryset:
        ivdata.append({json.dumps(i.optionsymbol.strike, cls=DecimalEncoder):float(100*i.imp_vol)})

    #print(optiondata)
    return JsonResponse(ivdata, safe=False)
"""
def ImpliedScreenerView(request):
    qs_ftse = Optionsymbol.objects.all().filter(expmonthdate__gte=date.today()).filter(asset='FTSE').values('asset','optiontype','expmonthdate').order_by('expmonthdate','optiontype').distinct()
    qs_alpha = Optionsymbol.objects.all().filter(expmonthdate__gte=date.today()).filter(asset='ALPHA').values('asset','optiontype','expmonthdate').order_by('expmonthdate','optiontype').distinct()
    qs_ote = Optionsymbol.objects.all().filter(expmonthdate__gte=date.today()).filter(asset='HTO').values('asset','optiontype','expmonthdate').order_by('expmonthdate','optiontype').distinct()
    qs_ete = Optionsymbol.objects.all().filter(expmonthdate__gte=date.today()).filter(asset='ETE').values('asset','optiontype','expmonthdate').order_by('expmonthdate','optiontype').distinct()
    qs_opap = Optionsymbol.objects.all().filter(expmonthdate__gte=date.today()).filter(asset='OPAP').values('asset','optiontype','expmonthdate').order_by('expmonthdate','optiontype').distinct()
    qs_deh = Optionsymbol.objects.all().filter(expmonthdate__gte=date.today()).filter(asset='PPC').values('asset','optiontype','expmonthdate').order_by('expmonthdate','optiontype').distinct()
    qs_peiraios = Optionsymbol.objects.all().filter(expmonthdate__gte=date.today()).filter(asset='TPEIR').values('asset','optiontype','expmonthdate').order_by('expmonthdate','optiontype').distinct()
    qs_ftse_count = qs_ftse.count()
    qs_alpha_count = qs_alpha.count()
    qs_ote_count = qs_alpha.count()
    qs_ete_count = qs_alpha.count()
    qs_opap_count = qs_alpha.count()
    qs_deh_count = qs_alpha.count()
    qs_peiraios_count = qs_alpha.count()
    context = {
        'qs_ftse' : qs_ftse,
        'qs_alpha' : qs_alpha,
        'qs_ote': qs_ote,
        'qs_ete': qs_ete,
        'qs_opap' : qs_opap,
        'qs_deh' : qs_deh,
        'qs_peiraios' : qs_peiraios,
        'qs_ftse_count' : qs_ftse_count,
        'qs_alpha_count' : qs_alpha_count,
        'qs_ote_count' : qs_ote_count,
        'qs_ete_count' : qs_ete_count,
        'qs_opap_count' : qs_opap_count,
        'qs_deh_count' : qs_deh_count,
        'qs_peiraios_count': qs_peiraios_count,
    }

    return render(request, 'option_pricing/ivscreeners.html', context)
"""
def ImpliedSmileView(request, asset, optiontype, expmonth, expyear):
    series = Option.objects.filter(optionsymbol__optionseries__asset=asset).filter(optionsymbol__optionseries__optiontype=optiontype).filter(optionsymbol__optionseries__expmonthdate__month=expmonth).filter(optionsymbol__optionseries__expmonthdate__year=expyear).order_by('-date')
    qs_asset = series[0].optionsymbol.optionseries.asset
    qs_optiontype = series[0].optionsymbol.optionseries.optiontype
    qs_month = series[0].optionsymbol.optionseries.expmonthdate.month
    qs_month_name = calendar.month_name[series[0].optionsymbol.optionseries.expmonthdate.month]
    qs_year = series[0].optionsymbol.optionseries.expmonthdate.year
    latest_trad_date = series[0].date.strftime("%#d-%#m-%Y")
    optionseries_id = series[0].optionsymbol.optionseries.id
    is_fav = False
    if series[0].optionsymbol.optionseries.seriesscreeners.filter(id=request.user.id).exists():
        is_fav = True
    context = {
        'series':series,
        'qs_asset':qs_asset,
        'qs_optiontype':qs_optiontype,
        'qs_month':qs_month,
        'qs_month_name':qs_month_name,
        'qs_year':qs_year,
        'latest_trad_date':latest_trad_date,
        'optionseries_id':optionseries_id,
        'is_fav':is_fav,
    }
    return render(request, 'option_pricing/ivsmile.html', context)

class ImpliedScreenerListCBV(View):
    def get(self, request):
        qs_ftse = Optionseries.objects.all().filter(expmonthdate__gte=date.today()).filter(asset='FTSE').order_by('expmonthdate','optiontype')
        qs_alpha = Optionseries.objects.all().filter(expmonthdate__gte=date.today()).filter(asset='ALPHA').order_by('expmonthdate','optiontype')
        qs_ote = Optionseries.objects.all().filter(expmonthdate__gte=date.today()).filter(asset='HTO').order_by('expmonthdate','optiontype')
        qs_ete = Optionseries.objects.all().filter(expmonthdate__gte=date.today()).filter(asset='ETE').order_by('expmonthdate','optiontype')
        qs_opap = Optionseries.objects.all().filter(expmonthdate__gte=date.today()).filter(asset='OPAP').order_by('expmonthdate','optiontype')
        qs_deh = Optionseries.objects.all().filter(expmonthdate__gte=date.today()).filter(asset='PPC').order_by('expmonthdate','optiontype')
        qs_peiraios = Optionseries.objects.all().filter(expmonthdate__gte=date.today()).filter(asset='TPEIR').order_by('expmonthdate','optiontype')
        qs_ftse_count = qs_ftse.count()
        qs_alpha_count = qs_alpha.count()
        qs_ote_count = qs_alpha.count()
        qs_ete_count = qs_alpha.count()
        qs_opap_count = qs_alpha.count()
        qs_deh_count = qs_alpha.count()
        qs_peiraios_count = qs_alpha.count()
        context = {
            'qs_ftse' : qs_ftse,
            'qs_alpha' : qs_alpha,
            'qs_ote': qs_ote,
            'qs_ete': qs_ete,
            'qs_opap' : qs_opap,
            'qs_deh' : qs_deh,
            'qs_peiraios' : qs_peiraios,
            'qs_ftse_count' : qs_ftse_count,
            'qs_alpha_count' : qs_alpha_count,
            'qs_ote_count' : qs_ote_count,
            'qs_ete_count' : qs_ete_count,
            'qs_opap_count' : qs_opap_count,
            'qs_deh_count' : qs_deh_count,
            'qs_peiraios_count': qs_peiraios_count,
        }

        return render(request, 'option_pricing/ivscreeners.html', context)
    
    def post(self, request, *args, **kwargs):
        if request.method == "POST":
            series_ids = request.POST.getlist('id[]')
            is_fav = False
            for id in series_ids:
                opt = Optionseries.objects.get(pk=id)
                if opt.seriesscreeners.filter(id=request.user.id).exists():
                    #opt.seriesscreeners.remove(request.user)
                    is_fav = False
                else:
                    opt.seriesscreeners.add(request.user)
                    is_fav = True
            return redirect('option_pricing:myseriesscreenerlistcbv')

class ImpliedScreenerATMListCBV(View):
    def get(self, request):
        qs_ftse = Optionseries.objects.all().filter(expmonthdate__gte=date.today()).filter(asset='FTSE').order_by('expmonthdate','optiontype')
        qs_alpha = Optionseries.objects.all().filter(expmonthdate__gte=date.today()).filter(asset='ALPHA').order_by('expmonthdate','optiontype')
        qs_ote = Optionseries.objects.all().filter(expmonthdate__gte=date.today()).filter(asset='HTO').order_by('expmonthdate','optiontype')
        qs_ete = Optionseries.objects.all().filter(expmonthdate__gte=date.today()).filter(asset='ETE').order_by('expmonthdate','optiontype')
        qs_opap = Optionseries.objects.all().filter(expmonthdate__gte=date.today()).filter(asset='OPAP').order_by('expmonthdate','optiontype')
        qs_deh = Optionseries.objects.all().filter(expmonthdate__gte=date.today()).filter(asset='PPC').order_by('expmonthdate','optiontype')
        qs_peiraios = Optionseries.objects.all().filter(expmonthdate__gte=date.today()).filter(asset='TPEIR').order_by('expmonthdate','optiontype')
        qs_ftse_count = qs_ftse.count()
        qs_alpha_count = qs_alpha.count()
        qs_ote_count = qs_alpha.count()
        qs_ete_count = qs_alpha.count()
        qs_opap_count = qs_alpha.count()
        qs_deh_count = qs_alpha.count()
        qs_peiraios_count = qs_alpha.count()
        
        atm_strikes_ftse, expmonth_atm_impvols_ftse = ([] for i in range(2))
        for i in qs_ftse:
            opt = Option.objects.filter(optionsymbol__optionseries = i)
            max_date = opt.aggregate(Max('date'))
            queryset = opt.filter(date=max_date['date__max'])
            atm_strikes_ftse.append(queryset[0].atm_strike)
        for i in qs_ftse:
            opt = Option.objects.filter(optionsymbol__optionseries = i)
            max_date = opt.aggregate(Max('date'))
            queryset = opt.filter(date=max_date['date__max'])
            expmonth_atm_impvols_ftse.append(float(100*(queryset[0].expmonth_atm_impvol)))
        atm_strikes_alpha, expmonth_atm_impvols_alpha = ([] for i in range(2))
        for i in qs_alpha:
            opt = Option.objects.filter(optionsymbol__optionseries = i)
            max_date = opt.aggregate(Max('date'))
            queryset = opt.filter(date=max_date['date__max'])
            atm_strikes_alpha.append(queryset[0].atm_strike)
        for i in qs_alpha:
            opt = Option.objects.filter(optionsymbol__optionseries = i)
            max_date = opt.aggregate(Max('date'))
            queryset = opt.filter(date=max_date['date__max'])
            expmonth_atm_impvols_alpha.append(float(100*(queryset[0].expmonth_atm_impvol)))
        atm_strikes_ote, expmonth_atm_impvols_ote = ([] for i in range(2))
        for i in qs_ote:
            opt = Option.objects.filter(optionsymbol__optionseries = i)
            max_date = opt.aggregate(Max('date'))
            queryset = opt.filter(date=max_date['date__max'])
            atm_strikes_ote.append(queryset[0].atm_strike)
        for i in qs_ote:
            opt = Option.objects.filter(optionsymbol__optionseries = i)
            max_date = opt.aggregate(Max('date'))
            queryset = opt.filter(date=max_date['date__max'])
            expmonth_atm_impvols_ote.append(float(100*(queryset[0].expmonth_atm_impvol)))
        atm_strikes_ete, expmonth_atm_impvols_ete = ([] for i in range(2))
        for i in qs_ete:
            opt = Option.objects.filter(optionsymbol__optionseries = i)
            max_date = opt.aggregate(Max('date'))
            queryset = opt.filter(date=max_date['date__max'])
            atm_strikes_ete.append(queryset[0].atm_strike)
        for i in qs_ete:
            opt = Option.objects.filter(optionsymbol__optionseries = i)
            max_date = opt.aggregate(Max('date'))
            queryset = opt.filter(date=max_date['date__max'])
            expmonth_atm_impvols_ete.append(float(100*(queryset[0].expmonth_atm_impvol)))
        atm_strikes_opap, expmonth_atm_impvols_opap = ([] for i in range(2))
        for i in qs_opap:
            opt = Option.objects.filter(optionsymbol__optionseries = i)
            max_date = opt.aggregate(Max('date'))
            queryset = opt.filter(date=max_date['date__max'])
            atm_strikes_opap.append(queryset[0].atm_strike)
        for i in qs_opap:
            opt = Option.objects.filter(optionsymbol__optionseries = i)
            max_date = opt.aggregate(Max('date'))
            queryset = opt.filter(date=max_date['date__max'])
            expmonth_atm_impvols_opap.append(float(100*(queryset[0].expmonth_atm_impvol)))
        atm_strikes_deh, expmonth_atm_impvols_deh = ([] for i in range(2))
        for i in qs_deh:
            opt = Option.objects.filter(optionsymbol__optionseries = i)
            max_date = opt.aggregate(Max('date'))
            queryset = opt.filter(date=max_date['date__max'])
            atm_strikes_deh.append(queryset[0].atm_strike)
        for i in qs_deh:
            opt = Option.objects.filter(optionsymbol__optionseries = i)
            max_date = opt.aggregate(Max('date'))
            queryset = opt.filter(date=max_date['date__max'])
            expmonth_atm_impvols_deh.append(float(100*(queryset[0].expmonth_atm_impvol)))
        atm_strikes_peiraios, expmonth_atm_impvols_peiraios = ([] for i in range(2))
        for i in qs_peiraios:
            opt = Option.objects.filter(optionsymbol__optionseries = i)
            max_date = opt.aggregate(Max('date'))
            queryset = opt.filter(date=max_date['date__max'])
            atm_strikes_peiraios.append(queryset[0].atm_strike)
        for i in qs_peiraios:
            opt = Option.objects.filter(optionsymbol__optionseries = i)
            max_date = opt.aggregate(Max('date'))
            queryset = opt.filter(date=max_date['date__max'])
            expmonth_atm_impvols_peiraios.append(float(100*(queryset[0].expmonth_atm_impvol)))

        context = {
            'qs_ftse' : qs_ftse,
            'qs_alpha' : qs_alpha,
            'qs_ote': qs_ote,
            'qs_ete': qs_ete,
            'qs_opap' : qs_opap,
            'qs_deh' : qs_deh,
            'qs_peiraios' : qs_peiraios,
            'qs_ftse_count' : qs_ftse_count,
            'qs_alpha_count' : qs_alpha_count,
            'qs_ote_count' : qs_ote_count,
            'qs_ete_count' : qs_ete_count,
            'qs_opap_count' : qs_opap_count,
            'qs_deh_count' : qs_deh_count,
            'qs_peiraios_count': qs_peiraios_count,
            'atm_strikes_ftse': atm_strikes_ftse,
            'expmonth_atm_impvols_ftse':expmonth_atm_impvols_ftse,
            'atm_strikes_alpha': atm_strikes_alpha,
            'expmonth_atm_impvols_alpha':expmonth_atm_impvols_alpha,
            'atm_strikes_ote': atm_strikes_ote,
            'expmonth_atm_impvols_ote':expmonth_atm_impvols_ote,
            'atm_strikes_ete': atm_strikes_ete,
            'expmonth_atm_impvols_ete':expmonth_atm_impvols_ete,
            'atm_strikes_opap': atm_strikes_opap,
            'expmonth_atm_impvols_opap':expmonth_atm_impvols_opap,
            'atm_strikes_deh': atm_strikes_deh,
            'expmonth_atm_impvols_deh':expmonth_atm_impvols_deh,
            'atm_strikes_peiraios': atm_strikes_peiraios,
            'expmonth_atm_impvols_peiraios':expmonth_atm_impvols_peiraios,
        }
        #print(expmonth_atm_impvols)

        return render(request, 'option_pricing/ivatmscreeners.html', context)
 
    def post(self, request, *args, **kwargs):
        if request.method == "POST":
            series_ids = request.POST.getlist('id[]')
            is_fav = False
            for id in series_ids:
                opt = Optionseries.objects.get(pk=id)
                if opt.seriesatmscreeners.filter(id=request.user.id).exists():
                    #opt.seriesscreeners.remove(request.user)
                    is_fav = False
                else:
                    opt.seriesatmscreeners.add(request.user)
                    is_fav = True
            return redirect('option_pricing:myseriesatmscreenerlistcbv')

def ImpliedATMView(request, asset, optiontype, expmonth, expyear):
    series = Option.objects.filter(optionsymbol__optionseries__asset=asset).filter(optionsymbol__optionseries__optiontype=optiontype).filter(optionsymbol__optionseries__expmonthdate__month=expmonth).filter(optionsymbol__optionseries__expmonthdate__year=expyear).order_by('-date')
    max_date = series.aggregate(Max('date'))
    queryset = series.filter(date=max_date['date__max']).order_by('optionsymbol__strike')
    qs_asset = series[0].optionsymbol.optionseries.asset
    qs_optiontype = series[0].optionsymbol.optionseries.optiontype
    qs_month = series[0].optionsymbol.optionseries.expmonthdate.month
    qs_month_name = calendar.month_name[series[0].optionsymbol.optionseries.expmonthdate.month]
    qs_year = series[0].optionsymbol.optionseries.expmonthdate.year
    latest_trad_date = series[0].date.strftime("%#d-%#m-%Y")
    optionseries_id = series[0].optionsymbol.optionseries.id
    is_fav = False
    if series[0].optionsymbol.optionseries.seriesatmscreeners.filter(id=request.user.id).exists():
        is_fav = True
    context = {
        'series':series,
        'qs_asset':qs_asset,
        'qs_optiontype':qs_optiontype,
        'qs_month':qs_month,
        'qs_month_name':qs_month_name,
        'qs_year':qs_year,
        'latest_trad_date':latest_trad_date,
        'optionseries_id':optionseries_id,
        'is_fav':is_fav,
    }
    return render(request, 'option_pricing/ivatm.html', context)

def IVATMChartView(request, asset, optiontype, expmonth, expyear):
    ivatmdata = []

    seriesid = Optionseries.objects.filter(asset=asset).filter(optiontype=optiontype).filter(expmonthdate__month=expmonth).filter(expmonthdate__year=expyear)
    option = Option.objects.filter(optionsymbol__optionseries__id=seriesid[0].id)
    qs = option.values('date').annotate(Avg('expmonth_atm_impvol')).order_by('date')
    
    list1=[]
    for i in range(len(qs)):
        list1.append(qs[i]['date'])

    list2=[]
    for i in range(len(qs)):
        list2.append(json.dumps(list1[i].strftime("%#d-%#m-%Y")))

    list3=[]
    for i in range(len(qs)):
        list3.append(qs[i]['expmonth_atm_impvol__avg'])

    list4=[]
    for i in range(len(qs)):
        list4.append(json.dumps(float(100*list3[i]), cls=DecimalEncoder))

    list5=[]
    for i in range(len(list2)):
        list5.append({list2[i]:list4[i]})
                                                                    
    #print(optiondata)
    return JsonResponse(list5, safe=False)

def OptionDailyStatsView(request):
    max_date = Optionvolume.objects.all().aggregate(Max('date'))
    
    context = {
        'max_date': max_date['date__max'].strftime("%#d-%#m-%Y"),
    }

    return render(request, 'option_pricing/optiondailystats.html', context)
"""
def OptionDailyGraphCallView(request):
    daily_volumes = []
    asset_names = ['FTSE', 'ALPHA', 'OTE', 'ETE', 'OPAP', 'DEH', 'PEIRAIOS']

    qs = Option.objects.all()
    max_date = qs.aggregate(Max('date'))
    queryset = qs.filter(date=max_date['date__max'])
    qs_ftse_call = queryset.filter(optionsymbol__asset='FTSE').filter(optionsymbol__optiontype='c').aggregate(Sum('volume'))
    daily_volumes.append(qs_ftse_call['volume__sum'])
    qs_alpha_call = queryset.filter(optionsymbol__asset='ALPHA').filter(optionsymbol__optiontype='c').aggregate(Sum('volume'))
    daily_volumes.append(qs_alpha_call['volume__sum'])
    qs_ote_call = queryset.filter(optionsymbol__asset='HTO').filter(optionsymbol__optiontype='c').aggregate(Sum('volume'))
    daily_volumes.append(qs_ote_call['volume__sum'])
    qs_ete_call = queryset.filter(optionsymbol__asset='ETE').filter(optionsymbol__optiontype='c').aggregate(Sum('volume'))
    daily_volumes.append(qs_ete_call['volume__sum'])
    qs_opap_call = queryset.filter(optionsymbol__asset='OPAP').filter(optionsymbol__optiontype='c').aggregate(Sum('volume'))
    daily_volumes.append(qs_opap_call['volume__sum'])
    qs_deh_call = queryset.filter(optionsymbol__asset='PPC').filter(optionsymbol__optiontype='c').aggregate(Sum('volume'))
    daily_volumes.append(qs_deh_call['volume__sum'])
    qs_peiraios_call = queryset.filter(optionsymbol__asset='TPEIR').filter(optionsymbol__optiontype='c').aggregate(Sum('volume'))
    daily_volumes.append(qs_peiraios_call['volume__sum'])

    daily_call_volumes=[]
    for i in range(len(daily_volumes)):
        daily_call_volumes.append({asset_names[i]:daily_volumes[i]})

    return JsonResponse(daily_call_volumes, safe=False)

def OptionDailyGraphPutView(request):
    daily_volumes = []
    asset_names = ['FTSE', 'ALPHA', 'OTE', 'ETE', 'OPAP', 'DEH', 'PEIRAIOS']

    qs = Option.objects.all()
    max_date = qs.aggregate(Max('date'))
    queryset = qs.filter(date=max_date['date__max'])
    qs_ftse_put = queryset.filter(optionsymbol__asset='FTSE').filter(optionsymbol__optiontype='p').aggregate(Sum('volume'))
    daily_volumes.append(qs_ftse_put['volume__sum'])
    qs_alpha_put = queryset.filter(optionsymbol__asset='ALPHA').filter(optionsymbol__optiontype='p').aggregate(Sum('volume'))
    daily_volumes.append(qs_alpha_put['volume__sum'])
    qs_ote_put = queryset.filter(optionsymbol__asset='HTO').filter(optionsymbol__optiontype='p').aggregate(Sum('volume'))
    daily_volumes.append(qs_ote_put['volume__sum'])
    qs_ete_put = queryset.filter(optionsymbol__asset='ETE').filter(optionsymbol__optiontype='p').aggregate(Sum('volume'))
    daily_volumes.append(qs_ete_put['volume__sum'])
    qs_opap_put = queryset.filter(optionsymbol__asset='OPAP').filter(optionsymbol__optiontype='p').aggregate(Sum('volume'))
    daily_volumes.append(qs_opap_put['volume__sum'])
    qs_deh_put = queryset.filter(optionsymbol__asset='PPC').filter(optionsymbol__optiontype='p').aggregate(Sum('volume'))
    daily_volumes.append(qs_deh_put['volume__sum'])
    qs_peiraios_put = queryset.filter(optionsymbol__asset='TPEIR').filter(optionsymbol__optiontype='p').aggregate(Sum('volume'))
    daily_volumes.append(qs_peiraios_put['volume__sum'])

    daily_put_volumes=[]
    for i in range(len(daily_volumes)):
        daily_put_volumes.append({asset_names[i]:daily_volumes[i]})

    return JsonResponse(daily_put_volumes, safe=False)

def OptionDailyVolumeGraphAllView(request):
    daily_volumes = []
    asset_names = ['FTSE', 'ALPHA', 'OTE', 'ETE', 'OPAP', 'DEH', 'PEIRAIOS']

    qs = Option.objects.all()
    max_date = qs.aggregate(Max('date'))
    queryset = qs.filter(date=max_date['date__max'])
    qs_ftse = queryset.filter(optionsymbol__asset='FTSE').aggregate(Sum('volume'))
    daily_volumes.append(qs_ftse['volume__sum'])
    qs_alpha = queryset.filter(optionsymbol__asset='ALPHA').aggregate(Sum('volume'))
    daily_volumes.append(qs_alpha['volume__sum'])
    qs_ote = queryset.filter(optionsymbol__asset='HTO').aggregate(Sum('volume'))
    daily_volumes.append(qs_ote['volume__sum'])
    qs_ete = queryset.filter(optionsymbol__asset='ETE').aggregate(Sum('volume'))
    daily_volumes.append(qs_ete['volume__sum'])
    qs_opap = queryset.filter(optionsymbol__asset='OPAP').aggregate(Sum('volume'))
    daily_volumes.append(qs_opap['volume__sum'])
    qs_deh = queryset.filter(optionsymbol__asset='PPC').aggregate(Sum('volume'))
    daily_volumes.append(qs_deh['volume__sum'])
    qs_peiraios = queryset.filter(optionsymbol__asset='TPEIR').aggregate(Sum('volume'))
    daily_volumes.append(qs_peiraios['volume__sum'])

    daily_call_volumes=[]
    for i in range(len(daily_volumes)):
        daily_call_volumes.append({asset_names[i]:daily_volumes[i]})

    return JsonResponse(daily_call_volumes, safe=False)

def OptionDailyVolumeGraphCallPutView(request):
    daily_volumes = []
    optiontypes = ['Calls', 'Puts']

    qs = Option.objects.all()
    max_date = qs.aggregate(Max('date'))
    queryset = qs.filter(date=max_date['date__max'])
    calls = queryset.filter(optionsymbol__optiontype='c').aggregate(Sum('volume'))
    daily_volumes.append(calls['volume__sum'])
    puts = queryset.filter(optionsymbol__optiontype='p').aggregate(Sum('volume'))
    daily_volumes.append(puts['volume__sum'])

    daily_call_put_volumes=[]
    for i in range(len(daily_volumes)):
        daily_call_put_volumes.append({optiontypes[i]:daily_volumes[i]})

    return JsonResponse(daily_call_put_volumes, safe=False)
"""


def OptionDailyGraphCallView(request):
    daily_volumes = []
    asset_names = ['FTSE', 'ALPHA', 'OTE', 'ETE', 'OPAP', 'DEH', 'PEIRAIOS']

    qs = Optionvolume.objects.all()
    max_date = qs.aggregate(Max('date'))
    queryset = qs.filter(date=max_date['date__max'])
    qs_ftse_call = queryset.filter(asset='FTSE').filter(optiontype='c').filter(expmonthdate__gte=F('date')).aggregate(Sum('volume'))
    daily_volumes.append(qs_ftse_call['volume__sum'])
    qs_alpha_call = queryset.filter(asset='ALPHA').filter(optiontype='c').filter(expmonthdate__gte=F('date')).aggregate(Sum('volume'))
    daily_volumes.append(qs_alpha_call['volume__sum'])
    qs_ote_call = queryset.filter(asset='HTO').filter(optiontype='c').filter(expmonthdate__gte=F('date')).aggregate(Sum('volume'))
    daily_volumes.append(qs_ote_call['volume__sum'])
    qs_ete_call = queryset.filter(asset='ETE').filter(optiontype='c').filter(expmonthdate__gte=F('date')).aggregate(Sum('volume'))
    daily_volumes.append(qs_ete_call['volume__sum'])
    qs_opap_call = queryset.filter(asset='OPAP').filter(optiontype='c').filter(expmonthdate__gte=F('date')).aggregate(Sum('volume'))
    daily_volumes.append(qs_opap_call['volume__sum'])
    qs_deh_call = queryset.filter(asset='PPC').filter(optiontype='c').filter(expmonthdate__gte=F('date')).aggregate(Sum('volume'))
    daily_volumes.append(qs_deh_call['volume__sum'])
    qs_peiraios_call = queryset.filter(asset='TPEIR').filter(optiontype='c').filter(expmonthdate__gte=F('date')).aggregate(Sum('volume'))
    daily_volumes.append(qs_peiraios_call['volume__sum'])

    daily_call_volumes=[]
    for i in range(len(daily_volumes)):
        daily_call_volumes.append({asset_names[i]:daily_volumes[i]})

    return JsonResponse(daily_call_volumes, safe=False)

def OptionDailyGraphPutView(request):
    daily_volumes = []
    asset_names = ['FTSE', 'ALPHA', 'OTE', 'ETE', 'OPAP', 'DEH', 'PEIRAIOS']

    qs = Optionvolume.objects.all()
    max_date = qs.aggregate(Max('date'))
    queryset = qs.filter(date=max_date['date__max'])
    qs_ftse_put = queryset.filter(asset='FTSE').filter(optiontype='p').filter(expmonthdate__gte=F('date')).aggregate(Sum('volume'))
    daily_volumes.append(qs_ftse_put['volume__sum'])
    qs_alpha_put = queryset.filter(asset='ALPHA').filter(optiontype='p').filter(expmonthdate__gte=F('date')).aggregate(Sum('volume'))
    daily_volumes.append(qs_alpha_put['volume__sum'])
    qs_ote_put = queryset.filter(asset='HTO').filter(optiontype='p').filter(expmonthdate__gte=F('date')).aggregate(Sum('volume'))
    daily_volumes.append(qs_ote_put['volume__sum'])
    qs_ete_put = queryset.filter(asset='ETE').filter(optiontype='p').filter(expmonthdate__gte=F('date')).aggregate(Sum('volume'))
    daily_volumes.append(qs_ete_put['volume__sum'])
    qs_opap_put = queryset.filter(asset='OPAP').filter(optiontype='p').filter(expmonthdate__gte=F('date')).aggregate(Sum('volume'))
    daily_volumes.append(qs_opap_put['volume__sum'])
    qs_deh_put = queryset.filter(asset='PPC').filter(optiontype='p').filter(expmonthdate__gte=F('date')).aggregate(Sum('volume'))
    daily_volumes.append(qs_deh_put['volume__sum'])
    qs_peiraios_put = queryset.filter(asset='TPEIR').filter(optiontype='p').filter(expmonthdate__gte=F('date')).aggregate(Sum('volume'))
    daily_volumes.append(qs_peiraios_put['volume__sum'])

    daily_put_volumes=[]
    for i in range(len(daily_volumes)):
        daily_put_volumes.append({asset_names[i]:daily_volumes[i]})

    return JsonResponse(daily_put_volumes, safe=False)

def OptionDailyVolumeGraphAllView(request):
    daily_volumes = []
    asset_names = ['FTSE', 'ALPHA', 'OTE', 'ETE', 'OPAP', 'DEH', 'PEIRAIOS']

    qs = Optionvolume.objects.all()
    max_date = qs.aggregate(Max('date'))
    queryset = qs.filter(date=max_date['date__max'])
    qs_ftse = queryset.filter(asset='FTSE').filter(expmonthdate__gte=F('date')).aggregate(Sum('volume'))
    daily_volumes.append(qs_ftse['volume__sum'])
    qs_alpha = queryset.filter(asset='ALPHA').filter(expmonthdate__gte=F('date')).aggregate(Sum('volume'))
    daily_volumes.append(qs_alpha['volume__sum'])
    qs_ote = queryset.filter(asset='HTO').filter(expmonthdate__gte=F('date')).aggregate(Sum('volume'))
    daily_volumes.append(qs_ote['volume__sum'])
    qs_ete = queryset.filter(asset='ETE').filter(expmonthdate__gte=F('date')).aggregate(Sum('volume'))
    daily_volumes.append(qs_ete['volume__sum'])
    qs_opap = queryset.filter(asset='OPAP').filter(expmonthdate__gte=F('date')).aggregate(Sum('volume'))
    daily_volumes.append(qs_opap['volume__sum'])
    qs_deh = queryset.filter(asset='PPC').filter(expmonthdate__gte=F('date')).aggregate(Sum('volume'))
    daily_volumes.append(qs_deh['volume__sum'])
    qs_peiraios = queryset.filter(asset='TPEIR').filter(expmonthdate__gte=F('date')).aggregate(Sum('volume'))
    daily_volumes.append(qs_peiraios['volume__sum'])

    daily_call_volumes=[]
    for i in range(len(daily_volumes)):
        daily_call_volumes.append({asset_names[i]:daily_volumes[i]})

    return JsonResponse(daily_call_volumes, safe=False)

def OptionDailyVolumeGraphCallPutView(request):
    daily_volumes = []
    optiontypes = ['Calls', 'Puts']

    qs = Optionvolume.objects.all()
    max_date = qs.aggregate(Max('date'))
    queryset = qs.filter(date=max_date['date__max'])
    calls = queryset.filter(optiontype='c').filter(expmonthdate__gte=F('date')).aggregate(Sum('volume'))
    daily_volumes.append(calls['volume__sum'])
    puts = queryset.filter(optiontype='p').filter(expmonthdate__gte=F('date')).aggregate(Sum('volume'))
    daily_volumes.append(puts['volume__sum'])

    daily_call_put_volumes=[]
    for i in range(len(daily_volumes)):
        daily_call_put_volumes.append({optiontypes[i]:daily_volumes[i]})

    return JsonResponse(daily_call_put_volumes, safe=False)

def OptionDailyVolumeGraphExpCallView(request):
    qs = Optionvolume.objects.all()
    max_date = qs.aggregate(Max('date'))
    queryset = qs.filter(optiontype='c').filter(expmonthdate__gte=F('date')).filter(date=max_date['date__max'])

    #fill in exp series
    exp = queryset.values('expmonthdate').order_by('expmonthdate').distinct()
    exp_series = []
    for i in range(len(exp)):
        exp_series.append(exp[i]['expmonthdate'])

    exp_series_list=[]
    for i in range(len(exp_series)):
        exp_series_list.append(exp_series[i].strftime("%B")+" "+exp_series[i].strftime("%Y"))

    exp_series_ = []
    for i in range(len(exp)):
        exp_series_.append(json.dumps(exp_series[i].strftime("%#Y-%#m-%d")))
        
    for item in range(len(exp_series_)):
        exp_series_[item]=exp_series_[item].replace('"', '')
        
    #fill in volume sums
    calls=[]  
    for i in range(len(exp_series_)):
        q = queryset.filter(expmonthdate=exp_series_[i]).aggregate(Sum('volume'))
        calls.append(q)
    
    calls_volume=[]
    for i in range(len(calls)):
        calls_volume.append(calls[i]['volume__sum'])

    #json dict
    daily_exp_series_volumes=[]
    for i in range(len(exp_series_list)):
        daily_exp_series_volumes.append({exp_series_list[i]:calls_volume[i]})

    return JsonResponse(daily_exp_series_volumes, safe=False)

def OptionDailyVolumeGraphExpPutView(request):
    qs = Optionvolume.objects.all()
    max_date = qs.aggregate(Max('date'))
    queryset = qs.filter(optiontype='p').filter(expmonthdate__gte=F('date')).filter(date=max_date['date__max'])

    #fill in exp series
    exp = queryset.values('expmonthdate').order_by('expmonthdate').distinct()
    exp_series = []
    for i in range(len(exp)):
        exp_series.append(exp[i]['expmonthdate'])

    exp_series_list=[]
    for i in range(len(exp_series)):
        exp_series_list.append(exp_series[i].strftime("%B")+" "+exp_series[i].strftime("%Y"))

    exp_series_ = []
    for i in range(len(exp)):
        exp_series_.append(json.dumps(exp_series[i].strftime("%#Y-%#m-%d")))
        
    for item in range(len(exp_series_)):
        exp_series_[item]=exp_series_[item].replace('"', '')
    
    #fill in volume sums
    puts=[]  
    for i in range(len(exp_series_)):
        q = queryset.filter(expmonthdate=exp_series_[i]).aggregate(Sum('volume'))
        puts.append(q)
    
    puts_volume=[]
    for i in range(len(puts)):
        puts_volume.append(puts[i]['volume__sum'])

    #json dict
    daily_exp_series_volumes=[]
    for i in range(len(exp_series_list)):
        daily_exp_series_volumes.append({exp_series_list[i]:puts_volume[i]})

    return JsonResponse(daily_exp_series_volumes, safe=False)

def OptionDailyOpenIntGraphCallView(request):
    qs = Optionvolume.objects.all()
    max_date = qs.aggregate(Max('date'))
    queryset = qs.filter(optiontype='c').filter(expmonthdate__gte=F('date')).filter(date=max_date['date__max'])

    #fill in exp series
    exp = queryset.values('expmonthdate').order_by('expmonthdate').distinct()
    exp_series = []
    for i in range(len(exp)):
        exp_series.append(exp[i]['expmonthdate'])

    exp_series_list=[]
    for i in range(len(exp_series)):
        exp_series_list.append(exp_series[i].strftime("%B")+" "+exp_series[i].strftime("%Y"))

    exp_series_ = []
    for i in range(len(exp)):
        exp_series_.append(json.dumps(exp_series[i].strftime("%#Y-%#m-%d")))
        
    for item in range(len(exp_series_)):
        exp_series_[item]=exp_series_[item].replace('"', '')
        
    #fill in open_int sums
    calls=[]  
    for i in range(len(exp_series_)):
        q = queryset.filter(expmonthdate=exp_series_[i]).aggregate(Sum('open_interest'))
        calls.append(q)
    
    calls_open_int=[]
    for i in range(len(calls)):
        calls_open_int.append(calls[i]['open_interest__sum'])

    #json dict
    daily_exp_series_open_ints=[]
    for i in range(len(exp_series_list)):
        daily_exp_series_open_ints.append({exp_series_list[i]:calls_open_int[i]})

    return JsonResponse(daily_exp_series_open_ints, safe=False)

def OptionDailyOpenIntGraphPutView(request):
    qs = Optionvolume.objects.all()
    max_date = qs.aggregate(Max('date'))
    queryset = qs.filter(optiontype='p').filter(expmonthdate__gte=F('date')).filter(date=max_date['date__max'])

    #fill in exp series
    exp = queryset.values('expmonthdate').order_by('expmonthdate').distinct()
    exp_series = []
    for i in range(len(exp)):
        exp_series.append(exp[i]['expmonthdate'])

    exp_series_list=[]
    for i in range(len(exp_series)):
        exp_series_list.append(exp_series[i].strftime("%B")+" "+exp_series[i].strftime("%Y"))

    exp_series_ = []
    for i in range(len(exp)):
        exp_series_.append(json.dumps(exp_series[i].strftime("%#Y-%#m-%d")))
        
    for item in range(len(exp_series_)):
        exp_series_[item]=exp_series_[item].replace('"', '')
    
    #fill in open_int sums
    puts=[]  
    for i in range(len(exp_series_)):
        q = queryset.filter(expmonthdate=exp_series_[i]).aggregate(Sum('open_interest'))
        puts.append(q)
    
    puts_open_int=[]
    for i in range(len(puts)):
        puts_open_int.append(puts[i]['open_interest__sum'])

    #json dict
    daily_exp_series_open_ints=[]
    for i in range(len(exp_series_list)):
        daily_exp_series_open_ints.append({exp_series_list[i]:puts_open_int[i]})

    return JsonResponse(daily_exp_series_open_ints, safe=False)

def unique(list1):
 
    # intilize a null list
    unique_list = []
     
    # traverse for all elements
    for x in list1:
        # check if exists in unique_list or not
        if x not in unique_list:
            unique_list.append(x)
    return(unique_list)

def OptionHistoricalStatsView(request):
    
    q = Optionvolume.objects.all()
    max_date = q.aggregate(Max('date'))
    queryset = q.filter(date=max_date['date__max'])

    assets=[]
    for i in range(len(queryset)):
        assets.append(queryset[i].get_asset_display())

    assets_=[]
    assets_ = sorted(unique(assets_))

    context = {
        'assets_': assets_,
    }

    return render(request, 'option_pricing/optionhiststats.html', context)
"""
def OptionHistVolumeGraphCallAllView(request):

    qs = Optionvolume.objects.all()
    queryset = qs.filter(optiontype='c').filter(expmonthdate__gte=F('date')) 
    dates = queryset.values('date').order_by('-date').distinct()[:252]  
    #fill in historical dates
    dates_volume=[]
    for i in range(len(dates)): 
        dates_volume.append(dates[i]['date']) 

    dates_volume_asc = sorted(dates_volume) 

    dates_volume_=[]
    for i in range(len(dates_volume_asc)): 
        dates_volume_.append(json.dumps(dates_volume_asc[i].strftime("%#Y-%#m-%d")))
    for item in range(len(dates_volume_)):                                  
        dates_volume_[item]=dates_volume_[item].replace('"', '') 
    #fill in volume sums
    calls=[]
    for i in range(len(dates_volume_)):
        q = queryset.filter(date=dates_volume_[i]).aggregate(Sum('volume'))
        calls.append(q)

    calls_volume=[]
    for i in range(len(calls)):
        calls_volume.append(calls[i]['volume__sum'])

    #json dict
    hist_call_volumes=[]
    for i in range(len(dates_volume_)):
        hist_call_volumes.append({dates_volume_[i]:calls_volume[i]})

    return JsonResponse(hist_call_volumes, safe=False)

def OptionHistVolumeGraphPutAllView(request):

    qs = Optionvolume.objects.all()
    queryset = qs.filter(optiontype='p').filter(expmonthdate__gte=F('date')) 
    dates = queryset.values('date').order_by('-date').distinct()[:252]  
    #fill in historical dates
    dates_volume=[]
    for i in range(len(dates)): 
        dates_volume.append(dates[i]['date']) 

    dates_volume_asc = sorted(dates_volume) 

    dates_volume_=[]
    for i in range(len(dates_volume_asc)): 
        dates_volume_.append(json.dumps(dates_volume_asc[i].strftime("%#Y-%#m-%d")))
    for item in range(len(dates_volume_)):                                  
        dates_volume_[item]=dates_volume_[item].replace('"', '') 
    #fill in volume sums
    puts=[]
    for i in range(len(dates_volume_)):
        q = queryset.filter(date=dates_volume_[i]).aggregate(Sum('volume'))
        puts.append(q)

    puts_volume=[]
    for i in range(len(puts)):
        puts_volume.append(puts[i]['volume__sum'])

    #json dict
    hist_put_volumes=[]
    for i in range(len(dates_volume_)):
        hist_put_volumes.append({dates_volume_[i]:puts_volume[i]})

    return JsonResponse(hist_put_volumes, safe=False)
"""

def OptionHistVolumeGraphCallAllView(request):

    queryset = Optionvolumeaggseriesasset.objects.filter(optiontype='c')
    dates = queryset.values('date').order_by('-date').distinct()[:252] 
    #fill in historical dates
    dates_volume=[]
    for i in range(len(dates)): 
        dates_volume.append(dates[i]['date']) 

    dates_volume_asc = sorted(dates_volume) 

    dates_volume_=[]
    for i in range(len(dates_volume_asc)): 
        dates_volume_.append(json.dumps(dates_volume_asc[i].strftime("%#Y-%#m-%d")))
    _dates_volume_=[]
    for i in range(len(dates_volume_asc)): 
        _dates_volume_.append(json.dumps(dates_volume_asc[i].strftime("%#d-%#m-%Y")))
    for item in range(len(_dates_volume_)):                                  
        _dates_volume_[item]=_dates_volume_[item].replace('"', '')
    for item in range(len(dates_volume_)):                                  
        dates_volume_[item]=dates_volume_[item].replace('"', '') 
    #fill in volume sums
    calls=[]
    for i in range(len(dates_volume_)):
        q = queryset.filter(date=dates_volume_[i]).aggregate(Sum('volume'))
        calls.append(q)

    calls_volume=[]
    for i in range(len(calls)):
        calls_volume.append(calls[i]['volume__sum'])

    #json dict
    hist_call_volumes=[]
    for i in range(len(_dates_volume_)):
        hist_call_volumes.append({_dates_volume_[i]:calls_volume[i]})

    return JsonResponse(hist_call_volumes, safe=False)


def OptionHistVolumeGraphPutAllView(request):

    queryset = Optionvolumeaggseriesasset.objects.filter(optiontype='p') 
    dates = queryset.values('date').order_by('-date').distinct()[:252]  
    #fill in historical dates
    dates_volume=[]
    for i in range(len(dates)): 
        dates_volume.append(dates[i]['date']) 

    dates_volume_asc = sorted(dates_volume) 

    dates_volume_=[]
    for i in range(len(dates_volume_asc)): 
        dates_volume_.append(json.dumps(dates_volume_asc[i].strftime("%#Y-%#m-%d")))
    for item in range(len(dates_volume_)):                                  
        dates_volume_[item]=dates_volume_[item].replace('"', '') 
    #fill in volume sums
    puts=[]
    for i in range(len(dates_volume_)):
        q = queryset.filter(date=dates_volume_[i]).aggregate(Sum('volume'))
        puts.append(q)

    puts_volume=[]
    for i in range(len(puts)):
        puts_volume.append(puts[i]['volume__sum'])

    #json dict
    hist_put_volumes=[]
    for i in range(len(dates_volume_)):
        hist_put_volumes.append({dates_volume_[i]:puts_volume[i]})

    return JsonResponse(hist_put_volumes, safe=False)

def assetidToAsset(assetid): 
    switcher = { 
        2: "ALPHA", 
        3: "ETE", 
        4: "FTSE", 
        5: "HTO", 
        6: "OPAP",
        7: "PPC", 
        8: "TPEIR", 
    } 
    return switcher.get(assetid)

def OptionHistVolumeGraphCallAssetView(request, assetid):

    asset_name = assetidToAsset(assetid)

    #qs = Optionvolume.objects.all()
    queryset = Optionvolumeaggseries.objects.filter(asset=asset_name).filter(optiontype='c')
    #queryset = qs.filter(asset=asset_name).filter(optiontype='c').filter(expmonthdate__gte=F('date')) 
    dates = queryset.values('date').order_by('-date').distinct()[:252]  
    #fill in historical dates
    dates_volume=[]
    for i in range(len(dates)): 
        dates_volume.append(dates[i]['date']) 

    dates_volume_asc = sorted(dates_volume) 

    dates_volume_=[]
    for i in range(len(dates_volume_asc)): 
        dates_volume_.append(json.dumps(dates_volume_asc[i].strftime("%#Y-%#m-%d")))
    for item in range(len(dates_volume_)):                                  
        dates_volume_[item]=dates_volume_[item].replace('"', '') 

    _dates_volume_=[]
    for i in range(len(dates_volume_asc)): 
        _dates_volume_.append(json.dumps(dates_volume_asc[i].strftime("%#d-%#m-%Y")))
    for item in range(len(_dates_volume_)):                                  
        _dates_volume_[item]=_dates_volume_[item].replace('"', '')

    #fill in volume sums
    calls=[]
    for i in range(len(dates_volume_)):
        q = queryset.filter(date=dates_volume_[i]).aggregate(Sum('volume'))
        calls.append(q)

    calls_volume=[]
    for i in range(len(calls)):
        calls_volume.append(calls[i]['volume__sum'])

    #json dict
    hist_call_volumes=[]
    for i in range(len(_dates_volume_)):
        hist_call_volumes.append({_dates_volume_[i]:calls_volume[i]})

    return JsonResponse(hist_call_volumes, safe=False)

def OptionHistVolumeGraphPutAssetView(request, assetid):

    asset_name = assetidToAsset(assetid)

    #qs = Optionvolume.objects.all()
    #queryset = qs.filter(asset=asset_name).filter(optiontype='p').filter(expmonthdate__gte=F('date'))
    queryset = Optionvolumeaggseries.objects.filter(asset=asset_name).filter(optiontype='p') 
    dates = queryset.values('date').order_by('-date').distinct()[:252]  
    #fill in historical dates
    dates_volume=[]
    for i in range(len(dates)): 
        dates_volume.append(dates[i]['date']) 

    dates_volume_asc = sorted(dates_volume) 

    dates_volume_=[]
    for i in range(len(dates_volume_asc)): 
        dates_volume_.append(json.dumps(dates_volume_asc[i].strftime("%#Y-%#m-%d")))
    for item in range(len(dates_volume_)):                                  
        dates_volume_[item]=dates_volume_[item].replace('"', '') 
    #fill in volume sums
    puts=[]
    for i in range(len(dates_volume_)):
        q = queryset.filter(date=dates_volume_[i]).aggregate(Sum('volume'))
        puts.append(q)

    puts_volume=[]
    for i in range(len(puts)):
        puts_volume.append(puts[i]['volume__sum'])

    #json dict
    hist_put_volumes=[]
    for i in range(len(dates_volume_)):
        hist_put_volumes.append({dates_volume_[i]:puts_volume[i]})

    return JsonResponse(hist_put_volumes, safe=False)

def OptionHistOpenIntGraphCallAllView(request):

    #qs = Optionvolume.objects.all()
    queryset = Optionvolumeaggseriesasset.objects.filter(optiontype='c')
    dates = queryset.values('date').order_by('-date').distinct()[:252]  
    #fill in historical dates
    dates_open_interest=[]
    for i in range(len(dates)): 
        dates_open_interest.append(dates[i]['date']) 

    dates_open_interest_asc = sorted(dates_open_interest) 

    dates_open_interest_=[]
    for i in range(len(dates_open_interest_asc)): 
        dates_open_interest_.append(json.dumps(dates_open_interest_asc[i].strftime("%#Y-%#m-%d")))
    for item in range(len(dates_open_interest_)):                                  
        dates_open_interest_[item]=dates_open_interest_[item].replace('"', '') 

    _dates_open_interest_=[]
    for i in range(len(dates_open_interest_asc)): 
        _dates_open_interest_.append(json.dumps(dates_open_interest_asc[i].strftime("%#d-%#m-%Y")))
    for item in range(len(_dates_open_interest_)):                                  
        _dates_open_interest_[item]=_dates_open_interest_[item].replace('"', '')

    #fill in volume sums
    calls=[]
    for i in range(len(dates_open_interest_)):
        q = queryset.filter(date=dates_open_interest_[i]).aggregate(Sum('open_interest'))
        calls.append(q)

    calls_open_interest=[]
    for i in range(len(calls)):
        calls_open_interest.append(calls[i]['open_interest__sum'])

    #json dict
    hist_call_open_interests=[]
    for i in range(len(_dates_open_interest_)):
        hist_call_open_interests.append({_dates_open_interest_[i]:calls_open_interest[i]})

    return JsonResponse(hist_call_open_interests, safe=False)

def OptionHistOpenIntGraphPutAllView(request):

    #qs = Optionvolume.objects.all()
    queryset = Optionvolumeaggseriesasset.objects.filter(optiontype='p') 
    dates = queryset.values('date').order_by('-date').distinct()[:252]  
    #fill in historical dates
    dates_open_interest=[]
    for i in range(len(dates)): 
        dates_open_interest.append(dates[i]['date']) 

    dates_open_interest_asc = sorted(dates_open_interest) 

    dates_open_interest_=[]
    for i in range(len(dates_open_interest_asc)): 
        dates_open_interest_.append(json.dumps(dates_open_interest_asc[i].strftime("%#Y-%#m-%d")))
    for item in range(len(dates_open_interest_)):                                  
        dates_open_interest_[item]=dates_open_interest_[item].replace('"', '') 
    #fill in open_interest sums
    puts=[]
    for i in range(len(dates_open_interest_)):
        q = queryset.filter(date=dates_open_interest_[i]).aggregate(Sum('open_interest'))
        puts.append(q)

    puts_open_interest=[]
    for i in range(len(puts)):
        puts_open_interest.append(puts[i]['open_interest__sum'])

    #json dict
    hist_put_open_interests=[]
    for i in range(len(dates_open_interest_)):
        hist_put_open_interests.append({dates_open_interest_[i]:puts_open_interest[i]})

    return JsonResponse(hist_put_open_interests, safe=False)

def OptionHistOpenIntGraphCallAssetView(request, assetid):

    asset_name = assetidToAsset(assetid)

    #qs = Optionvolume.objects.all()
    #queryset = qs.filter(asset=asset_name).filter(optiontype='c').filter(expmonthdate__gte=F('date')) 
    queryset = Optionvolumeaggseries.objects.filter(asset=asset_name).filter(optiontype='c')
    dates = queryset.values('date').order_by('-date').distinct()[:252]  
    #fill in historical dates
    dates_open_interest=[]
    for i in range(len(dates)): 
        dates_open_interest.append(dates[i]['date']) 

    dates_open_interest_asc = sorted(dates_open_interest) 

    dates_open_interest_=[]
    for i in range(len(dates_open_interest_asc)): 
        dates_open_interest_.append(json.dumps(dates_open_interest_asc[i].strftime("%#Y-%#m-%d")))
    for item in range(len(dates_open_interest_)):                                  
        dates_open_interest_[item]=dates_open_interest_[item].replace('"', '') 

    _dates_open_interest_=[]
    for i in range(len(dates_open_interest_asc)): 
        _dates_open_interest_.append(json.dumps(dates_open_interest_asc[i].strftime("%#d-%#m-%Y")))
    for item in range(len(_dates_open_interest_)):                                  
        _dates_open_interest_[item]=_dates_open_interest_[item].replace('"', '') 

    #fill in volume sums
    calls=[]
    for i in range(len(dates_open_interest_)):
        q = queryset.filter(date=dates_open_interest_[i]).aggregate(Sum('open_interest'))
        calls.append(q)

    calls_open_interest=[]
    for i in range(len(calls)):
        calls_open_interest.append(calls[i]['open_interest__sum'])

    #json dict
    hist_call_open_interests=[]
    for i in range(len(_dates_open_interest_)):
        hist_call_open_interests.append({_dates_open_interest_[i]:calls_open_interest[i]})

    return JsonResponse(hist_call_open_interests, safe=False)

def OptionHistOpenIntGraphPutAssetView(request, assetid):

    asset_name = assetidToAsset(assetid)

    #qs = Optionvolume.objects.all()
    #queryset = qs.filter(asset=asset_name).filter(optiontype='p').filter(expmonthdate__gte=F('date')) 
    queryset = Optionvolumeaggseries.objects.filter(asset=asset_name).filter(optiontype='p')
    dates = queryset.values('date').order_by('-date').distinct()[:252]  
    #fill in historical dates
    dates_open_interest=[]
    for i in range(len(dates)): 
        dates_open_interest.append(dates[i]['date']) 

    dates_open_interest_asc = sorted(dates_open_interest) 

    dates_open_interest_=[]
    for i in range(len(dates_open_interest_asc)): 
        dates_open_interest_.append(json.dumps(dates_open_interest_asc[i].strftime("%#Y-%#m-%d")))
    for item in range(len(dates_open_interest_)):                                  
        dates_open_interest_[item]=dates_open_interest_[item].replace('"', '') 
    #fill in volume sums
    calls=[]
    for i in range(len(dates_open_interest_)):
        q = queryset.filter(date=dates_open_interest_[i]).aggregate(Sum('open_interest'))
        calls.append(q)

    calls_open_interest=[]
    for i in range(len(calls)):
        calls_open_interest.append(calls[i]['open_interest__sum'])

    #json dict
    hist_call_open_interests=[]
    for i in range(len(dates_open_interest_)):
        hist_call_open_interests.append({dates_open_interest_[i]:calls_open_interest[i]})

    return JsonResponse(hist_call_open_interests, safe=False)
"""
def OptionCallPutMonthlyRatioAllView(request):
    
    ratio = Optioncallputmonthlyratio.objects.all()
    dates = ratio.values('date').order_by('date')[:24]

    dates_list=[]
    for i in range(len(dates)):
        dates_list.append(dates[i]['date'])

    dates_list_asc = sorted(dates_list)

    dates_list_=[]
    for i in range(len(dates_list_asc)):
        dates_list_.append(json.dumps(dates_list_asc[i].strftime("%B")+" "+dates_list_asc[i].strftime("%Y")))

    for item in range(len(dates_list_)):
        dates_list_[item]=dates_list_[item].replace('"', '')

    callputratio=[]
    for i in range(len(dates_list_asc)):
        q = ratio.filter(date=dates_list_asc[i]).aggregate(Sum('callputratio')) 
        callputratio.append(q)

    callputratio_=[]
    for i in range(len(callputratio)):
        callputratio_.append(callputratio[i]['callputratio__sum'])

    callputratiodata = []

    for i in dates_list_:
        callputratiodata.append({dates_list_[i]:json.dumps(callputratio_[i], cls=DecimalEncoder)})
        
    print(callputratiodata)
    return JsonResponse(callputratiodata, safe=False)
"""
def OptionCallPutMonthlyRatioAllView(request):
    callputratiodata = []

    ratio = Optioncallputmonthlyratio.objects.all()

    for i in ratio:
        callputratiodata.append({json.dumps(i.date.strftime("%B")+" "+i.date.strftime("%Y")):json.dumps(i.callputratio, cls=DecimalEncoder)})

    #print(optiondata)
    return JsonResponse(callputratiodata, safe=False)

def FutureDailyStatsView(request):
    max_date = Future.objects.all().aggregate(Max('date'))
    
    context = {
        'max_date': max_date['date__max'].strftime("%#d-%#m-%Y"),
    }

    return render(request, 'option_pricing/futuredailystats.html', context)

def FutureDailyGraphVolumeView(request):
    
    qs = Future.objects.all()
    max_date = qs.aggregate(Max('date'))
    queryset = qs.filter(date=max_date['date__max'])
    assetids = queryset.values('futuresymbol').distinct()  
    
    assetids_=[]
    for i in range(len(assetids)):
        assetids_.append(assetids[i]['futuresymbol'])

    assets=[]
    for i in range(len(assetids_)):
        assets.append(Futuresymbol.objects.filter(id=assetids_[i]))
        
    assets_fullname = []
    for i in range(len(assets)):
        assets_fullname.append(assets[i][0].get_asset_display())

    assets_=[]
    for i in range(len(assets)):
        assets_.append(assets[i][0].asset)

    asset_list = unique(assets_)
    asset_list_fullname = unique(assets_fullname)

    vols=[]
    for i in range(len(asset_list)):
	    vols.append(queryset.filter(futuresymbol__asset=asset_list[i]).filter(futuresymbol__expmonthdate__gte=F('date')).aggregate(Sum('volume')))

    vol_sums=[]
    for i in range(len(vols)):
        vol_sums.append(vols[i]['volume__sum'])

    daily_sum_volumes=[]
    for i in range(len(asset_list_fullname)):
        daily_sum_volumes.append({asset_list_fullname[i]:vol_sums[i]})

    return JsonResponse(daily_sum_volumes, safe=False)

def FutureDailyVolumeGraphExpAllView(request):
    qs = Future.objects.all()
    max_date = qs.aggregate(Max('date'))
    queryset = qs.filter(date=max_date['date__max']).exclude(futuresymbol__asset='FTSE')
    assetids = queryset.values('futuresymbol').distinct()  
    #fill in series months
    assetids_=[]
    for i in range(len(assetids)):
        assetids_.append(assetids[i]['futuresymbol'])

    symbols=[]
    for i in range(len(assetids_)):
        symbols.append(Futuresymbol.objects.filter(id=assetids_[i]))
        
    expseries = []
    for i in range(len(symbols)):
        expseries.append(symbols[i][0].expmonthdate)

    expseries_list = sorted(unique(expseries)) 

    expseries_ = []
    for i in range(len(expseries_list)):
        expseries_.append(json.dumps(expseries_list[i].strftime("%B")+" "+expseries_list[i].strftime("%Y"))) 
    #fill in volume sums
    vols=[]
    for i in range(len(expseries_list)):
        vols.append(queryset.filter(futuresymbol__expmonthdate=expseries_list[i]).aggregate(Sum('volume')))

    vol_sums=[]
    for i in range(len(vols)):
        vol_sums.append(vols[i]['volume__sum'])
    #json dict
    series_sum_volumes=[]
    for i in range(len(expseries_)):
        series_sum_volumes.append({expseries_[i]:vol_sums[i]})

    return JsonResponse(series_sum_volumes, safe=False)

def FutureDailyVolumeGraphExpFtseView(request):
    qs = Future.objects.all()
    max_date = qs.aggregate(Max('date'))
    queryset = qs.filter(date=max_date['date__max']).filter(futuresymbol__asset='FTSE')
    assetids = queryset.values('futuresymbol').distinct()  
    #fill in series months
    assetids_=[]
    for i in range(len(assetids)):
        assetids_.append(assetids[i]['futuresymbol'])

    symbols=[]
    for i in range(len(assetids_)):
        symbols.append(Futuresymbol.objects.filter(id=assetids_[i]))
        
    expseries = []
    for i in range(len(symbols)):
        expseries.append(symbols[i][0].expmonthdate)

    expseries_list = sorted(unique(expseries))

    expseries_ = []
    for i in range(len(expseries_list)):
        expseries_.append(json.dumps(expseries_list[i].strftime("%B")+" "+expseries_list[i].strftime("%Y"))) 
    #fill in volume sums
    vols=[]
    for i in range(len(expseries_list)):
        vols.append(queryset.filter(futuresymbol__expmonthdate=expseries_list[i]).aggregate(Sum('volume')))

    vol_sums=[]
    for i in range(len(vols)):
        vol_sums.append(vols[i]['volume__sum'])
    #json dict
    series_sum_volumes=[]
    for i in range(len(expseries_)):
        series_sum_volumes.append({expseries_[i]:vol_sums[i]})

    return JsonResponse(series_sum_volumes, safe=False)

def FutureDailyGraphOpenIntView(request):
    
    qs = Future.objects.all()
    max_date = qs.aggregate(Max('date'))
    queryset = qs.filter(date=max_date['date__max'])
    assetids = queryset.values('futuresymbol').distinct()  
    
    assetids_=[]
    for i in range(len(assetids)):
        assetids_.append(assetids[i]['futuresymbol'])

    assets=[]
    for i in range(len(assetids_)):
        assets.append(Futuresymbol.objects.filter(id=assetids_[i]))
        
    assets_fullname = []
    for i in range(len(assets)):
        assets_fullname.append(assets[i][0].get_asset_display())

    assets_=[]
    for i in range(len(assets)):
        assets_.append(assets[i][0].asset)

    asset_list = unique(assets_)
    asset_list_fullname = unique(assets_fullname)

    openints=[]
    for i in range(len(asset_list)):
	    openints.append(queryset.filter(futuresymbol__asset=asset_list[i]).filter(futuresymbol__expmonthdate__gte=F('date')).aggregate(Sum('open_interest')))

    openint_sums=[]
    for i in range(len(openints)):
        openint_sums.append(openints[i]['open_interest__sum'])

    daily_sum_openints=[]
    for i in range(len(asset_list_fullname)):
        daily_sum_openints.append({asset_list_fullname[i]:openint_sums[i]})

    return JsonResponse(daily_sum_openints, safe=False)

def FutureHistoricalStatsView(request):
    
    q = Future.objects.all()
    max_date = q.aggregate(Max('date'))
    queryset = q.filter(date=max_date['date__max'])

    _assets=[]
    for i in range(len(queryset)):
        _assets.append(queryset[i].futuresymbol.asset)

    assets_=[]
    assets_ = sorted(unique(_assets))

    context = {
        'assets_': assets_,
    }

    return render(request, 'option_pricing/futurehiststats.html', context)

def FutureHistVolumeGraphAllView(request):

    queryset = Futurevolumeaggasset.objects.all()
    dates = queryset.values('date').order_by('-date').distinct()[:252] 
    #fill in historical dates
    dates_volume=[]
    for i in range(len(dates)): 
        dates_volume.append(dates[i]['date']) 

    dates_volume_asc = sorted(dates_volume) 

    dates_volume_=[]
    for i in range(len(dates_volume_asc)): 
        dates_volume_.append(json.dumps(dates_volume_asc[i].strftime("%#Y-%#m-%d")))
    _dates_volume_=[]
    for i in range(len(dates_volume_asc)): 
        _dates_volume_.append(json.dumps(dates_volume_asc[i].strftime("%#d-%#m-%Y")))
    for item in range(len(_dates_volume_)):                                  
        _dates_volume_[item]=_dates_volume_[item].replace('"', '')
    for item in range(len(dates_volume_)):                                  
        dates_volume_[item]=dates_volume_[item].replace('"', '') 
    #fill in volume sums
    futures=[]
    for i in range(len(dates_volume_)):
        q = queryset.filter(date=dates_volume_[i]).aggregate(Sum('volume'))
        futures.append(q)

    futures_volume=[]
    for i in range(len(futures)):
        futures_volume.append(futures[i]['volume__sum'])

    #json dict
    hist_call_volumes=[]
    for i in range(len(_dates_volume_)):
        hist_call_volumes.append({_dates_volume_[i]:futures_volume[i]})

    return JsonResponse(hist_call_volumes, safe=False)

def FutureHistOpenIntGraphAllView(request):

    queryset = Futurevolumeaggasset.objects.all()
    dates = queryset.values('date').order_by('-date').distinct()[:252] 
    #fill in historical dates
    dates_volume=[]
    for i in range(len(dates)): 
        dates_volume.append(dates[i]['date']) 

    dates_volume_asc = sorted(dates_volume) 

    dates_volume_=[]
    for i in range(len(dates_volume_asc)): 
        dates_volume_.append(json.dumps(dates_volume_asc[i].strftime("%#Y-%#m-%d")))
    _dates_volume_=[]
    for i in range(len(dates_volume_asc)): 
        _dates_volume_.append(json.dumps(dates_volume_asc[i].strftime("%#d-%#m-%Y")))
    for item in range(len(_dates_volume_)):                                  
        _dates_volume_[item]=_dates_volume_[item].replace('"', '')
    for item in range(len(dates_volume_)):                                  
        dates_volume_[item]=dates_volume_[item].replace('"', '') 
    #fill in volume sums
    futures=[]
    for i in range(len(dates_volume_)):
        q = queryset.filter(date=dates_volume_[i]).aggregate(Sum('open_interest'))
        futures.append(q)

    futures_volume=[]
    for i in range(len(futures)):
        futures_volume.append(futures[i]['open_interest__sum'])

    #json dict
    hist_call_volumes=[]
    for i in range(len(_dates_volume_)):
        hist_call_volumes.append({_dates_volume_[i]:futures_volume[i]})

    return JsonResponse(hist_call_volumes, safe=False)

def FutureHistAssetView(request, asset):
    underlying = asset

    q = Future.objects.all()
    max_date = q.aggregate(Max('date'))
    queryset = q.filter(date=max_date['date__max'])

    #assets=[]
    _assets=[]
    for i in range(len(queryset)):
        #assets.append(queryset[i].futuresymbol.get_asset_display())
        _assets.append(queryset[i].futuresymbol.asset)

    assets_=[]
    assets_ = sorted(unique(_assets))

    context = {
        'assets_': assets_,
        #'_assets': _assets,
        'underlying': underlying,
    }

    return render(request, 'option_pricing/futurehistassetstats.html', context)

def FutureHistVolumeGraphAssetView(request, asset):

    #queryset = Future.objects.filter(futuresymbol__asset=asset)
    queryset = Futurevolumeaggasset.objects.filter(asset=asset)
    dates = queryset.values('date').order_by('-date').distinct()[:252]  
    #fill in historical dates
    dates_volume=[]
    for i in range(len(dates)): 
        dates_volume.append(dates[i]['date']) 

    dates_volume_asc = sorted(dates_volume) 

    dates_volume_=[]
    for i in range(len(dates_volume_asc)): 
        dates_volume_.append(json.dumps(dates_volume_asc[i].strftime("%#Y-%#m-%d")))
    for item in range(len(dates_volume_)):                                  
        dates_volume_[item]=dates_volume_[item].replace('"', '') 

    _dates_volume_=[]
    for i in range(len(dates_volume_asc)): 
        _dates_volume_.append(json.dumps(dates_volume_asc[i].strftime("%#d-%#m-%Y")))
    for item in range(len(_dates_volume_)):                                  
        _dates_volume_[item]=_dates_volume_[item].replace('"', '')

    #fill in volume sums
    volumes=[]
    for i in range(len(dates_volume_)):
        q = queryset.filter(date=dates_volume_[i]).aggregate(Sum('volume'))
        volumes.append(q)

    calls_volume=[]
    for i in range(len(volumes)):
        calls_volume.append(volumes[i]['volume__sum'])

    #json dict
    hist_call_volumes=[]
    for i in range(len(_dates_volume_)):
        hist_call_volumes.append({_dates_volume_[i]:calls_volume[i]})

    return JsonResponse(hist_call_volumes, safe=False)

def FutureHistOpenIntGraphAssetView(request, asset):

    #queryset = Future.objects.filter(futuresymbol__asset=asset)
    queryset = Futurevolumeaggasset.objects.filter(asset=asset)
    dates = queryset.values('date').order_by('-date').distinct()[:252]  
    #fill in historical dates
    dates_volume=[]
    for i in range(len(dates)): 
        dates_volume.append(dates[i]['date']) 

    dates_volume_asc = sorted(dates_volume) 

    dates_volume_=[]
    for i in range(len(dates_volume_asc)): 
        dates_volume_.append(json.dumps(dates_volume_asc[i].strftime("%#Y-%#m-%d")))
    for item in range(len(dates_volume_)):                                  
        dates_volume_[item]=dates_volume_[item].replace('"', '') 

    _dates_volume_=[]
    for i in range(len(dates_volume_asc)): 
        _dates_volume_.append(json.dumps(dates_volume_asc[i].strftime("%#d-%#m-%Y")))
    for item in range(len(_dates_volume_)):                                  
        _dates_volume_[item]=_dates_volume_[item].replace('"', '')

    #fill in volume sums
    volumes=[]
    for i in range(len(dates_volume_)):
        q = queryset.filter(date=dates_volume_[i]).aggregate(Sum('open_interest'))
        volumes.append(q)

    calls_volume=[]
    for i in range(len(volumes)):
        calls_volume.append(volumes[i]['open_interest__sum'])

    #json dict
    hist_call_volumes=[]
    for i in range(len(_dates_volume_)):
        hist_call_volumes.append({_dates_volume_[i]:calls_volume[i]})

    return JsonResponse(hist_call_volumes, safe=False)

def OptionSymbolExportCSV(request, optionsymbol):
    response = HttpResponse(content_type='text/csv')

    writer = csv.writer(response)
    writer.writerow(['Symbol', 'Date', 'Closing price', 'Change', 'Volume', 'Max', 'Min', 'Trades', 'Fixing price', 'Open interest'])

    qs = Optioncsv.objects.filter(trading_symbol=optionsymbol).order_by('date')

    for i in qs.values_list('trading_symbol', 'date', 'closing_price', 'change', 'volume', 'max', 'min', 'trades', 'fixing_price', 'open_interest'):
        writer.writerow(i)

    response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(str(optionsymbol))
    return response

def FutureSymbolExportCSV(request, futuresymbol):
    response = HttpResponse(content_type='text/csv')

    writer = csv.writer(response)
    writer.writerow(['Symbol', 'Date', 'Closing price', 'Change', 'Volume', 'Max', 'Min', 'Trades', 'Fixing price', 'Open interest'])

    qs = Futurecsv.objects.filter(symbol=futuresymbol).order_by('date')

    for i in qs.values_list('symbol', 'date', 'closing_price', 'change', 'volume', 'max', 'min', 'trades', 'fixing_price', 'open_interest'):
        writer.writerow(i)

    response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(str(futuresymbol))
    return response

def OptionSearchSymbolView(request):
    form = OptionSearchForm()
    q = ''
    results = []
    option_results = Optionsymbol.objects.all()
    results_length = len(option_results)
    future_results = Futuresymbol.objects.all()
    stock_results = Stocksymbol.objects.all()


    if 'q' in request.GET:
        form = OptionSearchForm(request.GET)
        if form.is_valid():
            q = form.cleaned_data['q']
            option_results = Optionsymbol.objects.filter(symbol__icontains=q).order_by('expmonthdate', 'strike')
            future_results = Futuresymbol.objects.filter(symbol__icontains=q)
            stock_results = Stocksymbol.objects.filter(symbol__icontains=q)
            results = chain(option_results, future_results, stock_results)
            results_length = len(option_results)

            paginator = Paginator(option_results, 10)
            page_number = request.GET.get('page', 1)
            page_obj = paginator.get_page(page_number)

            return render(request, 'option_pricing/option_symbol_search.html',
                        {'form': form,
                        'q': q,
                        'results': results,                       
                        'option_results': option_results,
                        'results_length': results_length,
                        'page_obj': page_obj,
                        'future_results': future_results,
                        'stock_results': stock_results,}) 

    else:
        return render(request, 'option_pricing/option_symbol_search.html',
                    {'form': form,
                    'q': q,
                    'results': results,}) 




""" def OptionSearchSymbolView2(request):
    form = OptionSearchForm2()
    if request.is_ajax():
        term = request.GET.get('term')
        symbols = Optionsymbol.objects.all().filter(symbol__icontains=term)
        symbols_json = JsonResponse(list(symbols.values()), safe=False)
        return symbols_json
    return render(request, 'option_pricing/option_symbol_search2.html', {'form': form}) """


def OptionSearchSymbolAutoCompleteView(request):
    if 'term' in request.GET:
        qs_options = Optionsymbol.objects.filter(symbol__icontains=request.GET.get('term'))
        qs_futures = Futuresymbol.objects.filter(symbol__icontains=request.GET.get('term'))
        qs_stocks = Stocksymbol.objects.filter(symbol__icontains=request.GET.get('term'))
        qs = chain(qs_options, qs_futures, qs_stocks)
        symbols = list()
        for item in qs:
            symbols.append(item.symbol)
        return JsonResponse(symbols, safe=False)
    return render(request, 'option_pricing/option_symbol_search.html')
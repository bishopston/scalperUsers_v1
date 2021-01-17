from django.shortcuts import render
from django.db.models import Max, Min
from django.core.paginator import Paginator
from django.http import JsonResponse

from datetime import datetime
import json

from .models import Option, Optionsymbol, Future, Futuresymbol
from .forms import OptionScreenerForm, FutureScreenerForm


def home(request):
    return render(request, 'option_pricing/home.html')

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
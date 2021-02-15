from django.shortcuts import render, redirect
from django.db.models import Max, Min, Avg
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.generic import View
from django.contrib.auth.decorators import login_required

from datetime import datetime, date
import calendar
import json
from decimal import Decimal

from .models import Option, Optionsymbol, Optionseries, Future, Futuresymbol
from accounts.models import CustomUser
from .forms import OptionScreenerForm, FutureScreenerForm, ImpliedperStrikeScreenerForm


def home(request):
    return render(request, 'option_pricing/home.html')
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

    
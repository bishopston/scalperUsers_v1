from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from django.http import HttpResponse, JsonResponse, Http404
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.views import View
from django.urls import reverse
import json
from validate_email import validate_email
from django.contrib.auth.password_validation import *
from django.template.loader import render_to_string
from django.db.models import Max, Min, Avg, Sum, F
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_protect, csrf_exempt

from accounts.forms import UserAdminCreationForm, CreatePortfolioForm, PortfolioOptionForm, PortfolioFutureForm, PortfolioStockForm, PortfolioOptionUpdateForm, PortfolioOptionUpdateModelForm, PortfolioFutureUpdateModelForm, PortfolioStockUpdateModelForm
from accounts.models import CustomUser, Portfolio, PortfolioOption, PortfolioFuture, PortfolioStock
from option_pricing.models import Option, Future, Stock, Optionsymbol, Futuresymbol, Stocksymbol, Optionseries
from accounts.validators import NumberValidator, UppercaseValidator, LowercaseValidator, SymbolValidator

from datetime import date, datetime
from decimal import Decimal

from django.template.loader import get_template
from xhtml2pdf import pisa

def register(request):
    if request.method == 'POST':
        form = UserAdminCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.set_password(form.cleaned_data['password1'])            
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'Martingale account activation'
            message = render_to_string('registration/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email.send()
            return HttpResponse('Thank you for registering at Martingale! An activation link has been sent to your email')                     
    else:
        form = UserAdminCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('accounts:login')
    else:
        return HttpResponse('Activation link is invalid!')

"""
#@login_required()
def register(request):
    form = UserAdminCreationForm()
    if request.method == 'POST':
        form = UserAdminCreationForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(email=email, password=raw_password)
            login(request, user)
            return redirect('option_pricing:home')
    return render(request, 'registration/register.html', {'form': form})
"""
class EmailValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data['email']
        if not validate_email(email):
            return JsonResponse({'email_error': 'Email is invalid'}, status=400)
        if CustomUser.objects.filter(email=email).exists():
            return JsonResponse({'email_error': 'sorry email in use,choose another one '}, status=409)
        return JsonResponse({'email_valid': True})

class PasswordValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        password = data['password1']
        if validate_password(password) is not None:
            return JsonResponse({'password1_error': 'Password is invalid'}, status=400)
        return JsonResponse({'password1_valid': True})


@ login_required
def favourite_list(request):
    fav_list = Optionsymbol.objects.filter(favourites=request.user)
    return render(request,
                  'accounts/favourites.html',
                  {'fav_list': fav_list})
"""
@ login_required
def favourite_add(request, id):
    optionsymbol = get_object_or_404(Optionsymbol, id=id)
    if optionsymbol.favourites.filter(id=request.user.id).exists():
        optionsymbol.favourites.remove(request.user)
    else:
        optionsymbol.favourites.add(request.user)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])
"""

@ login_required
def favourite_add(request, id):
    data = {'success': True} 
    if request.POST.get('action') == 'post':
        print('mitsos')
        print(request.method)
        print(request.body)
        data = json.loads(request.body)
        print(data)
        """
        if request.is_ajax():
            id = int(request.POST.get('optionsymbolid'))
            optionsymbol = get_object_or_404(Optionsymbol, id=id)
            if optionsymbol.favourites.filter(id=request.user.id).exists():
                optionsymbol.favourites.remove(request.user)
                optionsymbol.save()
                data['success'] = True
                print(optionsymbol)
            else:
                optionsymbol.favourites.add(request.user)
                optionsymbol.save()
                data['success'] = True
                print(optionsymbol)
                """
    else:
        print('mitsoulas')
        print(request.method)
    return JsonResponse(data)
"""
@ login_required
def like_option(request):
    option = get_object_or_404(Optionsymbol, id=request.POST.get('optionsymbol_id'))
    is_liked = False
    if option.likes.filter(id=request.user.id).exists():
        option.likes.remove(request.user)
        is_liked = False
    else:
        option.likes.add(request.user)
        is_liked = True
    #option.save()
    return HttpResponseRedirect(option.get_absolute_url())
"""
@ login_required
def like_list(request):
    like_list = Optionsymbol.objects.filter(likes=request.user)
    return render(request,
                  'accounts/likes.html',
                  {'like_list': like_list})

@ login_required
def like_option(request):
    option = get_object_or_404(Optionsymbol, id=request.POST.get('id'))
    optionsymbol_id = option.id
    is_liked = False
    if option.likes.filter(id=request.user.id).exists():
        option.likes.remove(request.user)
        is_liked = False
    else:
        option.likes.add(request.user)
        is_liked = True
    #option.save()
    context = {
        'is_liked': is_liked,
        'optionsymbol_id' : optionsymbol_id,
        'total_likes' : option.total_likes(),
    }
    if request.is_ajax():
        html = render_to_string('accounts/like_section.html', context, request=request)
        return JsonResponse({'form' : html})

@ login_required
def myOptionScreeners(request):
    option = get_object_or_404(Optionsymbol, id=request.POST.get('id'))
    optionsymbol_id = option.id
    is_fav = False
    if option.optionscreeners.filter(id=request.user.id).exists():
        option.optionscreeners.remove(request.user)
        is_fav = False
    else:
        option.optionscreeners.add(request.user)
        is_fav = True
    #option.save()
    context = {
        'is_fav': is_fav,
        'optionsymbol_id' : optionsymbol_id,
    }
    if request.is_ajax():
        html = render_to_string('accounts/myoptionscreeners_section.html', context, request=request)
        return JsonResponse({'form' : html})

@ login_required
def myOptionList(request):
    myoptionlist = Optionsymbol.objects.filter(optionscreeners=request.user).order_by('asset', '-expmonthdate', 'optiontype', 'strike')
    myoptionlist_count = myoptionlist.count()

    opt_latest_trad_date, opt_closing_prices, opt_changes, opt_volumes, opt_trades, opt_open_interests = ([] for i in range(6))

    for i in myoptionlist:
        opt = Option.objects.filter(optionsymbol__symbol = i)
        max_date = opt.aggregate(Max('date'))
        queryset = opt.filter(date=max_date['date__max'])
        opt_latest_trad_date.append(queryset[0].date.strftime("%d-%m-%Y"))
        opt_closing_prices.append(queryset[0].closing_price)
        opt_changes.append(queryset[0].change)
        opt_volumes.append(queryset[0].volume)
        opt_trades.append(queryset[0].trades)
        opt_open_interests.append(queryset[0].open_interest)


    context = {
        'myoptionlist': myoptionlist,
        'myoptionlist_count': myoptionlist_count,
        'opt_latest_trad_date': opt_latest_trad_date,
        'opt_closing_prices': opt_closing_prices,
        'opt_changes': opt_changes,
        'opt_volumes': opt_volumes,
        'opt_trades': opt_trades,
        'opt_open_interests': opt_open_interests,
    }

    return render(request,
                  'accounts/myoptionlist2.html',
                  context)

@ login_required
def myFutureScreeners(request):
    future = get_object_or_404(Futuresymbol, id=request.POST.get('id'))
    futuresymbol_id = future.id
    is_fav = False
    if future.futurescreeners.filter(id=request.user.id).exists():
        future.futurescreeners.remove(request.user)
        is_fav = False
    else:
        future.futurescreeners.add(request.user)
        is_fav = True
    #option.save()
    context = {
        'is_fav': is_fav,
        'futuresymbol_id' : futuresymbol_id,
    }
    if request.is_ajax():
        html = render_to_string('accounts/myfuturescreeners_section.html', context, request=request)
        return JsonResponse({'form' : html})

@ login_required
def myFutureList(request):
    myfuturelist = Futuresymbol.objects.filter(futurescreeners=request.user).order_by('asset', '-expmonthdate')
    myfuturelist_count = myfuturelist.count()

    fut_latest_trad_date, fut_closing_prices, fut_changes, fut_volumes, fut_trades, fut_open_interests = ([] for i in range(6))

    for i in myfuturelist:
        fut = Future.objects.filter(futuresymbol__symbol = i)
        max_date = fut.aggregate(Max('date'))
        queryset = fut.filter(date=max_date['date__max'])
        fut_latest_trad_date.append(queryset[0].date.strftime("%d-%m-%Y"))
        fut_closing_prices.append(queryset[0].closing_price)
        fut_changes.append(queryset[0].change)
        fut_volumes.append(queryset[0].volume)
        fut_trades.append(queryset[0].trades)
        fut_open_interests.append(queryset[0].open_interest)


    context = {
        'myfuturelist': myfuturelist,
        'myfuturelist_count': myfuturelist_count,
        'fut_latest_trad_date': fut_latest_trad_date,
        'fut_closing_prices': fut_closing_prices,
        'fut_changes': fut_changes,
        'fut_volumes': fut_volumes,
        'fut_trades': fut_trades,
        'fut_open_interests': fut_open_interests,
    }

    return render(request,
                  'accounts/myfuturelist2.html',
                  context)

@ login_required
def myImpliedList(request):
    myimpliedlist = Optionseries.objects.filter(seriesscreeners=request.user).order_by('asset', '-expmonthdate', 'optiontype')
    myimpliedlist_count = myimpliedlist.count()

    iv_latest_trad_date, iv_strike_number = ([] for i in range(2))

    for i in myimpliedlist:
        iv = Option.objects.filter(optionsymbol__optionseries = i)
        max_date = iv.aggregate(Max('date'))
        queryset = iv.filter(date=max_date['date__max'])
        iv_strike_number.append(len(queryset))
        iv_latest_trad_date.append(queryset[0].date.strftime("%d-%m-%Y"))

    context = {
        'myimpliedlist_count': myimpliedlist_count,
        'iv_latest_trad_date': iv_latest_trad_date,
        'iv_strike_number': iv_strike_number,
        'myimpliedlist': myimpliedlist
    }

    return render(request,
                  'accounts/myimplied2.html',
                  context)

@ login_required
def myImpliedScreeners(request):
    series = get_object_or_404(Optionseries, id=request.POST.get('id'))
    optionseries_id = series.id
    is_fav = False
    if series.seriesscreeners.filter(id=request.user.id).exists():
        series.seriesscreeners.remove(request.user)
        is_fav = False
    else:
        series.seriesscreeners.add(request.user)
        is_fav = True
    #option.save()
    context = {
        'is_fav': is_fav,
        'optionseries_id' : optionseries_id,
    }
    if request.is_ajax():
        html = render_to_string('accounts/myimpliedscreeners_section.html', context, request=request)
        return JsonResponse({'form' : html})

@ login_required
def myImpliedATMList(request):
    myimpliedatmlist = Optionseries.objects.filter(seriesatmscreeners=request.user).order_by('asset', '-expmonthdate', 'optiontype')
    myimpliedatmlist_count = myimpliedatmlist.count()

    atm_iv_latest_trad_date, atm_iv_strike_number, atm_strikes, atm_ivs = ([] for i in range(4))

    for i in myimpliedatmlist:
        atm_iv = Option.objects.filter(optionsymbol__optionseries = i)
        max_date = atm_iv.aggregate(Max('date'))
        queryset = atm_iv.filter(date=max_date['date__max'])
        atm_iv_strike_number.append(len(queryset))
        atm_iv_latest_trad_date.append(queryset[0].date.strftime("%d-%m-%Y"))
        atm_strikes.append(queryset[0].atm_strike)
        atm_ivs.append(float(100*(queryset[0].expmonth_atm_impvol)))

    context = {
        'myimpliedatmlist_count': myimpliedatmlist_count,
        'atm_iv_latest_trad_date': atm_iv_latest_trad_date,
        'atm_iv_strike_number': atm_iv_strike_number,
        'atm_strikes': atm_strikes,
        'atm_ivs': atm_ivs,
        'myimpliedatmlist': myimpliedatmlist
    }
    return render(request,
                  'accounts/myimpliedatm.html',
                  context)

@ login_required
def myImpliedATMScreeners(request):
    series = get_object_or_404(Optionseries, id=request.POST.get('id'))
    optionseries_id = series.id
    is_fav = False
    if series.seriesatmscreeners.filter(id=request.user.id).exists():
        series.seriesatmscreeners.remove(request.user)
        is_fav = False
    else:
        series.seriesatmscreeners.add(request.user)
        is_fav = True
    #option.save()
    context = {
        'is_fav': is_fav,
        'optionseries_id' : optionseries_id,
    }
    if request.is_ajax():
        html = render_to_string('accounts/myimpliedatmscreeners_section.html', context, request=request)
        return JsonResponse({'form' : html})

@ login_required
def PortfolioView(request):
    myportfolios = Portfolio.objects.filter(creator=request.user)

    portfolio_active_options_count=[]
    for i in range(len(myportfolios)):
        portfolio_active_options_count.append(myportfolios[i].active_option_count())

    portfolio_active_futures_count=[]
    for i in range(len(myportfolios)):
        portfolio_active_futures_count.append(myportfolios[i].active_future_count())

    portfolio_stocks_count=[]
    for i in range(len(myportfolios)):
        portfolio_stocks_count.append(myportfolios[i].stock_count())

    form = CreatePortfolioForm()
    if request.method == "POST":
        form = CreatePortfolioForm(request.POST)
        if form.is_valid():
            portfolio = Portfolio(
                name = form.cleaned_data["name"],
                creator = request.user
            )
            portfolio.save()
        return HttpResponseRedirect(reverse('accounts:portfolio'))

    context = {'myportfolios': myportfolios,
                'form': form,
                'portfolio_active_options_count': portfolio_active_options_count,
                'portfolio_active_futures_count': portfolio_active_futures_count,
                'portfolio_stocks_count': portfolio_stocks_count}

    return render(request, 'accounts/myportfolios.html', context)

@ login_required
def DeletePortfolioView(request):
    if request.method == "POST":
        portfolio_ids = request.POST.getlist('id[]')
        for id in portfolio_ids:
            portfolio = Portfolio.objects.get(pk=id)
            portfolio.delete()
        return redirect('accounts:portfolio')

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return json.JSONEncoder.default(self, obj)

@ login_required
def PortfolioDetailView(request, portfolio_id):
    portfolio = Portfolio.objects.get(pk=portfolio_id)
    options = PortfolioOption.objects.filter(portfolio=portfolio_id)
    futures = PortfolioFuture.objects.filter(portfolio=portfolio_id)
    stocks = PortfolioStock.objects.filter(portfolio=portfolio_id)
    portfolioOptionForm = PortfolioOptionForm()
    portfolioFutureForm = PortfolioFutureForm()
    portfolioStockForm = PortfolioStockForm()

    active_options=[]
    for i in range(len(options)):
        if options[i].active_option():
            active_options.append(options[i])

    active_futures=[]
    for i in range(len(futures)):
        if futures[i].active_future():
            active_futures.append(futures[i])

    max_options_dates, options_clos_prices, stock_prices, profits, option_debit_credit, option_valuation, option_payoff, option_delta, option_contracts = ([] for i in range(9))

    for i in active_options:
        qs_options = Option.objects.filter(optionsymbol=PortfolioOption.objects.get(id=i.id).optionsymbol.id)
        max_options_date = qs_options.aggregate(Max('date'))
        option_strike = json.dumps(qs_options[0].optionsymbol.strike, cls=DecimalEncoder)
        option_type = qs_options[0].optionsymbol.optiontype

        max_options_dates.append(max_options_date['date__max'].strftime("%#d/%#m/%Y"))

        latest_clos = qs_options.filter(date=max_options_date['date__max']).values('closing_price')[0]['closing_price']
        options_clos_prices.append(json.dumps(latest_clos, cls=DecimalEncoder))

        latest_stock = qs_options.filter(date=max_options_date['date__max']).values('stock')[0]['stock']
        stock_prices.append(json.dumps(latest_stock, cls=DecimalEncoder))

        latest_delta = qs_options.filter(date=max_options_date['date__max']).values('delta')[0]['delta']    

        if i.optionsymbol.asset == 'FTSE':
            if option_type == 'c':
                if i.position == 'Long':
                    profits.append(float(latest_stock) - float(qs_options[0].optionsymbol.strike) - float(i.buysellprice))
                    option_payoff.append(float(2*i.contracts*(float(latest_stock) - float(qs_options[0].optionsymbol.strike) - float(i.buysellprice))))
                else:
                    profits.append(float(qs_options[0].optionsymbol.strike) + float(i.buysellprice) - float(latest_stock))
                    option_payoff.append(float(2*i.contracts*(float(qs_options[0].optionsymbol.strike) + float(i.buysellprice) - float(latest_stock))))

            if option_type == 'p':
                if i.position == 'Long':                
                    profits.append(float(qs_options[0].optionsymbol.strike) - float(latest_stock) - float(i.buysellprice))
                    option_payoff.append(float(2*i.contracts*(float(qs_options[0].optionsymbol.strike) - float(latest_stock) - float(i.buysellprice))))
                else:
                    profits.append(float(latest_stock) + float(i.buysellprice) - float(qs_options[0].optionsymbol.strike))
                    option_payoff.append(float(2*i.contracts*(float(latest_stock) + float(i.buysellprice) - float(qs_options[0].optionsymbol.strike))))

        else:
            if option_type == 'c':
                if i.position == 'Long':
                    profits.append(float(latest_stock) - float(qs_options[0].optionsymbol.strike) - float(i.buysellprice))
                    option_payoff.append(float(100*i.contracts*(float(latest_stock) - float(qs_options[0].optionsymbol.strike) - float(i.buysellprice))))
                else:
                    profits.append(float(qs_options[0].optionsymbol.strike) + float(i.buysellprice) - float(latest_stock))
                    option_payoff.append(float(100*i.contracts*(float(qs_options[0].optionsymbol.strike) + float(i.buysellprice) - float(latest_stock))))
                    

            if option_type == 'p':
                if i.position == 'Long':                
                    profits.append(float(qs_options[0].optionsymbol.strike) - float(latest_stock) - float(i.buysellprice))
                    option_payoff.append(float(100*i.contracts*(float(qs_options[0].optionsymbol.strike) - float(latest_stock) - float(i.buysellprice))))
                else:
                    profits.append(float(latest_stock) + float(i.buysellprice) - float(qs_options[0].optionsymbol.strike))
                    option_payoff.append(float(100*i.contracts*(float(latest_stock) + float(i.buysellprice) - float(qs_options[0].optionsymbol.strike))))

        if i.optionsymbol.asset == 'FTSE':
            if i.position == 'Long':
                option_debit_credit.append(-float(2*i.contracts*i.buysellprice))
            else:
                option_debit_credit.append(float(2*i.contracts*i.buysellprice))
            option_valuation.append(float(2*i.contracts*latest_clos))
            option_delta.append(float(i.contracts*latest_delta))
            option_contracts.append(float(i.contracts))
        else:
            if i.position == 'Long':
                option_debit_credit.append(-float(100*i.contracts*i.buysellprice))
            else:
                option_debit_credit.append(float(100*i.contracts*i.buysellprice))
            option_valuation.append(float(100*i.contracts*latest_clos))      
            option_delta.append(float(i.contracts*latest_delta))
            option_contracts.append(float(i.contracts))      

    max_futures_dates, futures_clos_prices, futures_stock_prices, fixing_prices, futures_profits, future_debit_credit, future_valuation, future_payoff, future_contracts = ([] for i in range(9))

    for i in active_futures:
        qs_futures = Future.objects.filter(futuresymbol=PortfolioFuture.objects.get(id=i.id).futuresymbol.id)
        max_futures_date = qs_futures.aggregate(Max('date'))

        max_futures_dates.append(max_futures_date['date__max'].strftime("%#d/%#m/%Y"))

        latest_clos = qs_futures.filter(date=max_futures_date['date__max']).values('closing_price')[0]['closing_price']
        futures_clos_prices.append(json.dumps(latest_clos, cls=DecimalEncoder))

        latest_stock = qs_futures.filter(date=max_futures_date['date__max']).values('stock')[0]['stock']
        futures_stock_prices.append(json.dumps(latest_stock, cls=DecimalEncoder))

        latest_fixing_price = qs_futures.filter(date=max_futures_date['date__max']).values('fixing_price')[0]['fixing_price']
        fixing_prices.append(json.dumps(latest_fixing_price, cls=DecimalEncoder))

        if i.futuresymbol.asset == 'FTSE':
            if i.position == 'Long':
                if latest_fixing_price > 0:
                    futures_profits.append(float(latest_fixing_price) - float(i.buysellprice))
                    future_payoff.append(float(2*i.contracts*(float(latest_fixing_price) - float(i.buysellprice))))
                else:
                    futures_profits.append(float(latest_clos) - float(i.buysellprice))
                    future_payoff.append(float(2*i.contracts*(float(latest_clos) - float(i.buysellprice))))

            if i.position == 'Short':
                if latest_fixing_price > 0:
                    futures_profits.append(float(i.buysellprice) - float(latest_fixing_price))
                    future_payoff.append(float(2*i.contracts*(float(i.buysellprice) - float(latest_fixing_price))))
                else:
                    futures_profits.append(float(i.buysellprice) - float(latest_clos))
                    future_payoff.append(float(2*i.contracts*(float(i.buysellprice) - float(latest_clos))))
                    
        else:
            if i.position == 'Long':
                if latest_fixing_price > 0:
                    futures_profits.append(float(latest_fixing_price) - float(i.buysellprice))
                    future_payoff.append(float(100*i.contracts*(float(latest_fixing_price) - float(i.buysellprice))))
                else:
                    futures_profits.append(float(latest_clos) - float(i.buysellprice))
                    future_payoff.append(float(100*i.contracts*(float(latest_clos) - float(i.buysellprice))))

            if i.position == 'Short':
                if latest_fixing_price > 0:
                    futures_profits.append(float(i.buysellprice) - float(latest_fixing_price))
                    future_payoff.append(float(100*i.contracts*(float(i.buysellprice) - float(latest_fixing_price))))
                else:
                    futures_profits.append(float(i.buysellprice) - float(latest_clos))
                    future_payoff.append(float(100*i.contracts*(float(i.buysellprice) - float(latest_clos))))

        if i.futuresymbol.asset == 'FTSE':
            if i.position == 'Long':
                future_debit_credit.append(-float(2*i.contracts*i.buysellprice))
            else:
                future_debit_credit.append(float(2*i.contracts*i.buysellprice))
            future_valuation.append(float(2*i.contracts*latest_clos))
            future_contracts.append(float(i.contracts))
        else:
            if i.position == 'Long':
                future_debit_credit.append(-float(100*i.contracts*i.buysellprice))
            else:
                future_debit_credit.append(float(100*i.contracts*i.buysellprice))
            future_valuation.append(float(100*i.contracts*latest_clos)) 
            future_contracts.append(float(i.contracts))

    max_stocks_dates, stock_stock_prices, stock_debit_credit, stocks_profits, stocks_valuation, stocks_total_payoff, stocks_quantity = ([] for i in range(7))

    for i in stocks:
        qs_stocks = Stock.objects.filter(stocksymbol=PortfolioStock.objects.get(id=i.id).stocksymbol.id)
        max_stocks_date = qs_stocks.aggregate(Max('date'))
        
        max_stocks_dates.append(max_stocks_date['date__max'].strftime("%#d/%#m/%Y"))
        
        latest_stock = qs_stocks.filter(date=max_stocks_date['date__max']).values('close')[0]['close']
        stock_stock_prices.append(json.dumps(latest_stock, cls=DecimalEncoder))
        stock_debit_credit.append(float(i.quantity*float(i.buyprice)))
        stocks_quantity.append(float(i.quantity))
        
        stocks_profits.append(float(latest_stock)-float(i.buyprice))
        stocks_valuation.append(float(i.quantity*latest_stock))
        stocks_total_payoff.append(float(i.quantity*(float(latest_stock)-float(i.buyprice))))

    if request.method == "POST":
        portfolioOptionForm = PortfolioOptionForm(request.POST)
        
        if portfolioOptionForm.is_valid():
            asset_ = request.POST.get('asset')
            optiontype_ = request.POST.get('option_type')
            expmonth_ = request.POST.get('exp_month')
            expyear_ = request.POST.get('exp_year')
            strike_ = request.POST.get('strike')
            expdate_ = request.POST.get('exp_date')
            try:
                qs = Optionsymbol.objects.filter(expmonthdate__gte=date.today()).filter(asset=asset_).filter(optiontype=optiontype_).filter(expmonthdate__month=expmonth_).filter(expmonthdate__year=expyear_).filter(strike=strike_)
                optionsymbol_ = qs[0]
                portfolioOption = PortfolioOption(
                    optionsymbol = optionsymbol_,
                    position = portfolioOptionForm.cleaned_data["position_type"],
                    contracts = portfolioOptionForm.cleaned_data["contracts"],
                    buysellprice = portfolioOptionForm.cleaned_data["buysellprice"],
                )
                
                portfolioOption.save()
                portfolioOption.portfolio.add(portfolio)

                return HttpResponseRedirect(request.path_info)            

            except (IndexError, Optionsymbol.DoesNotExist):
                return render(request, 'accounts/myportfolio-detail.html', {
                    'portfolio': portfolio,
                    'options': options,
                    'futures': futures,
                    'stocks': stocks,
                    'active_options': active_options,
                    'active_options_count': len(active_options),
                    'active_futures': active_futures,
                    'active_futures_count': len(active_futures),
                    'portfolioOptionForm': portfolioOptionForm,
                    'portfolioFutureForm': portfolioFutureForm,
                    'portfolioStockForm': portfolioStockForm,
                    'max_options_dates': max_options_dates,   
                    'options_clos_prices': options_clos_prices,     
                    'stock_prices': stock_prices,       
                    'profits': profits,  
                    'option_debit_credit': option_debit_credit,
                    'option_valuation': option_valuation,
                    'option_payoff': option_payoff,
                    'option_delta': option_delta,
                    'max_futures_dates': max_futures_dates, 
                    'futures_clos_prices': futures_clos_prices,
                    'futures_stock_prices': futures_stock_prices,
                    'max_stocks_dates': max_stocks_dates,
                    'fixing_prices': fixing_prices,
                    'futures_profits': futures_profits,
                    'future_debit_credit': future_debit_credit,
                    'future_valuation': future_valuation,
                    'future_payoff': future_payoff,
                    'max_stocks_dates': max_stocks_dates,
                    'stock_stock_prices': stock_stock_prices,
                    'stock_debit_credit': stock_debit_credit,
                    'stocks_profits': stocks_profits,
                    'stocks_valuation': stocks_valuation,
                    'stocks_total_payoff': stocks_total_payoff,
                    'stocks_count': len(stocks),
                    'stocks_quantity': sum(stocks_quantity),
                    'total_portfolio_valuation': sum(option_valuation)+sum(future_valuation)+sum(stocks_valuation),
                    'total_portfolio_payoff': sum(option_payoff)+sum(future_payoff)+sum(stocks_total_payoff),
                    'total_option_contracts': sum(option_contracts),
                    'total_option_debit_credit': sum(option_debit_credit),
                    'total_option_valuation': sum(option_valuation),
                    'total_option_payoff': sum(option_payoff),
                    'total_option_delta': sum(option_delta),
                    'total_future_contracts': sum(future_contracts),
                    'total_future_debit_credit': sum(future_debit_credit),
                    'total_future_valuation': sum(future_valuation),
                    'total_future_payoff': sum(future_payoff),
                    'total_stock_debit_credit': sum(stock_debit_credit),
                    'total_stock_valuation': sum(stocks_valuation),
                    'total_stock_payoff': sum(stocks_total_payoff),
                    'today': date.today(),
                    'error_message': 'Please select a valid not expired option',
                    })


    context = {'portfolio': portfolio,
                'options': options,
                'futures': futures,
                'stocks': stocks,
                'active_options': active_options,
                'active_options_count': len(active_options),
                'active_futures': active_futures,
                'active_futures_count': len(active_futures),
                'portfolioOptionForm': portfolioOptionForm,
                'portfolioFutureForm': portfolioFutureForm,
                'portfolioStockForm': portfolioStockForm,
                'max_options_dates': max_options_dates,
                'options_clos_prices': options_clos_prices,
                'stock_prices': stock_prices,
                'profits': profits,
                'option_debit_credit': option_debit_credit,
                'option_valuation': option_valuation,
                'option_payoff': option_payoff,
                'option_delta': option_delta,
                'max_futures_dates': max_futures_dates, 
                'futures_clos_prices': futures_clos_prices,
                'futures_stock_prices': futures_stock_prices,
                'fixing_prices': fixing_prices,
                'futures_profits': futures_profits,
                'future_debit_credit': future_debit_credit,
                'future_valuation': future_valuation,
                'future_payoff': future_payoff,
                'max_stocks_dates': max_stocks_dates,
                'stock_stock_prices': stock_stock_prices,
                'stock_debit_credit': stock_debit_credit,
                'stocks_profits': stocks_profits,
                'stocks_valuation': stocks_valuation,
                'stocks_total_payoff': stocks_total_payoff,
                'stocks_count': len(stocks),
                'stocks_quantity': sum(stocks_quantity),
                'total_portfolio_valuation': sum(option_valuation)+sum(future_valuation)+sum(stocks_valuation),
                'total_portfolio_payoff': sum(option_payoff)+sum(future_payoff)+sum(stocks_total_payoff),
                'total_option_contracts': sum(option_contracts),
                'total_option_debit_credit': sum(option_debit_credit),
                'total_option_valuation': sum(option_valuation),
                'total_option_payoff': sum(option_payoff),
                'total_option_delta': sum(option_delta),
                'total_future_contracts': sum(future_contracts),
                'total_future_debit_credit': sum(future_debit_credit),
                'total_future_valuation': sum(future_valuation),
                'total_future_payoff': sum(future_payoff),
                'total_stock_debit_credit': sum(stock_debit_credit),
                'total_stock_valuation': sum(stocks_valuation),
                'total_stock_payoff': sum(stocks_total_payoff),
                'today': date.today(),
                }

    return render(request, 'accounts/myportfolio-detail.html', context)

@ login_required
def DeletePortfolioOptionView(request):
    #portfolioOptionUpdateForm = PortfolioOptionUpdateForm()
    if request.method == "POST":
        portfoliooption_ids = request.POST.getlist('id[]')
        portfolio_id = request.POST.get('portfolio_id')
        for id in portfoliooption_ids:
            portfoliooption = PortfolioOption.objects.get(pk=id)
            portfoliooption.delete()
        return redirect(reverse('accounts:portfolio-detail', kwargs={ 'portfolio_id': portfolio_id, }))
    #print(portfolio_id)
    #return HttpResponseRedirect(reverse('accounts:portfolio-detail', args=(portfolio_id)))
    #return redirect('/accounts/portfolio/portfolio_id/')

@ login_required
def UpdatePortfolioOptionView(request, portfolio_id, portfoliooption_id):
    portfoliooption = PortfolioOption.objects.get(pk=portfoliooption_id)
    symbol = portfoliooption.optionsymbol.symbol
    portfolioOptionUpdateForm = PortfolioOptionUpdateModelForm(instance=portfoliooption)

    if request.method == 'POST':
        portfolioOptionUpdateForm = PortfolioOptionUpdateModelForm(request.POST, instance=portfoliooption)
        if portfolioOptionUpdateForm.is_valid():
            portfolioOptionUpdateForm.save()
            return redirect(reverse('accounts:portfolio-detail', kwargs={ 'portfolio_id': portfolio_id, }))

    return render(request, 'accounts/myportfoliooption-update.html', {'portfoliooption':portfoliooption, 'portfolioOptionUpdateForm': portfolioOptionUpdateForm, 'symbol':symbol,})


@ login_required
def DeletePortfolioFutureView(request):
    if request.method == "POST":
        portfoliofuture_ids = request.POST.getlist('id[]')
        portfolio_id = request.POST.get('portfolio_id')
        for id in portfoliofuture_ids:
            portfoliofuture = PortfolioFuture.objects.get(pk=id)
            portfoliofuture.delete()
        return redirect(reverse('accounts:portfolio-detail', kwargs={ 'portfolio_id': portfolio_id, }))
    #print(portfolio_id)
    #return HttpResponseRedirect(reverse('accounts:portfolio-detail', args=(portfolio_id)))
    #return redirect('/accounts/portfolio/portfolio_id/')

@ login_required
def UpdatePortfolioFutureView(request, portfolio_id, portfoliofuture_id):
    portfoliofuture = PortfolioFuture.objects.get(pk=portfoliofuture_id)
    symbol = portfoliofuture.futuresymbol.symbol
    portfolioFutureUpdateForm = PortfolioFutureUpdateModelForm(instance=portfoliofuture)

    if request.method == 'POST':
        portfolioFutureUpdateForm = PortfolioFutureUpdateModelForm(request.POST, instance=portfoliofuture)
        if portfolioFutureUpdateForm.is_valid():
            portfolioFutureUpdateForm.save()
        return redirect(reverse('accounts:portfolio-detail', kwargs={ 'portfolio_id': portfolio_id, }))

    return render(request, 'accounts/myportfoliofuture-update.html', {'portfoliofuture':portfoliofuture, 'portfolioFutureUpdateForm': portfolioFutureUpdateForm, 'symbol':symbol,})

@ login_required
def PortfolioFutureDetailView(request, portfolio_id):

    portfolio = Portfolio.objects.get(pk=portfolio_id)
    options = PortfolioOption.objects.filter(portfolio=portfolio_id)
    futures = PortfolioFuture.objects.filter(portfolio=portfolio_id)
    stocks = PortfolioStock.objects.filter(portfolio=portfolio_id)
    portfolioOptionForm = PortfolioOptionForm()
    portfolioFutureForm = PortfolioFutureForm()
    portfolioStockForm = PortfolioStockForm()

    active_options=[]
    for i in range(len(options)):
        if options[i].active_option():
            active_options.append(options[i])

    active_futures=[]
    for i in range(len(futures)):
        if futures[i].active_future():
            active_futures.append(futures[i])

    max_options_dates, options_clos_prices, stock_prices, profits, option_debit_credit, option_valuation, option_payoff, option_delta, option_contracts = ([] for i in range(9))

    for i in active_options:
        qs_options = Option.objects.filter(optionsymbol=PortfolioOption.objects.get(id=i.id).optionsymbol.id)
        max_options_date = qs_options.aggregate(Max('date'))
        option_strike = json.dumps(qs_options[0].optionsymbol.strike, cls=DecimalEncoder)
        option_type = qs_options[0].optionsymbol.optiontype

        max_options_dates.append(max_options_date['date__max'].strftime("%#d/%#m/%Y"))

        latest_clos = qs_options.filter(date=max_options_date['date__max']).values('closing_price')[0]['closing_price']
        options_clos_prices.append(json.dumps(latest_clos, cls=DecimalEncoder))

        latest_stock = qs_options.filter(date=max_options_date['date__max']).values('stock')[0]['stock']
        stock_prices.append(json.dumps(latest_stock, cls=DecimalEncoder))

        latest_delta = qs_options.filter(date=max_options_date['date__max']).values('delta')[0]['delta']
        #option_delta.append(json.dumps(latest_delta, cls=DecimalEncoder)) 

        if i.optionsymbol.asset == 'FTSE':
            if option_type == 'c':
                if i.position == 'Long':
                    profits.append(float(latest_stock) - float(qs_options[0].optionsymbol.strike) - float(i.buysellprice))
                    option_payoff.append(float(2*i.contracts*(float(latest_stock) - float(qs_options[0].optionsymbol.strike) - float(i.buysellprice))))
                else:
                    profits.append(float(qs_options[0].optionsymbol.strike) + float(i.buysellprice) - float(latest_stock))
                    option_payoff.append(float(2*i.contracts*(float(qs_options[0].optionsymbol.strike) + float(i.buysellprice) - float(latest_stock))))

            if option_type == 'p':
                if i.position == 'Long':                
                    profits.append(float(qs_options[0].optionsymbol.strike) - float(latest_stock) - float(i.buysellprice))
                    option_payoff.append(float(2*i.contracts*(float(qs_options[0].optionsymbol.strike) - float(latest_stock) - float(i.buysellprice))))
                else:
                    profits.append(float(latest_stock) + float(i.buysellprice) - float(qs_options[0].optionsymbol.strike))
                    option_payoff.append(float(2*i.contracts*(float(latest_stock) + float(i.buysellprice) - float(qs_options[0].optionsymbol.strike))))

        else:
            if option_type == 'c':
                if i.position == 'Long':
                    profits.append(float(latest_stock) - float(qs_options[0].optionsymbol.strike) - float(i.buysellprice))
                    option_payoff.append(float(100*i.contracts*(float(latest_stock) - float(qs_options[0].optionsymbol.strike) - float(i.buysellprice))))
                else:
                    profits.append(float(qs_options[0].optionsymbol.strike) + float(i.buysellprice) - float(latest_stock))
                    option_payoff.append(float(100*i.contracts*(float(qs_options[0].optionsymbol.strike) + float(i.buysellprice) - float(latest_stock))))
                    

            if option_type == 'p':
                if i.position == 'Long':                
                    profits.append(float(qs_options[0].optionsymbol.strike) - float(latest_stock) - float(i.buysellprice))
                    option_payoff.append(float(100*i.contracts*(float(qs_options[0].optionsymbol.strike) - float(latest_stock) - float(i.buysellprice))))
                else:
                    profits.append(float(latest_stock) + float(i.buysellprice) - float(qs_options[0].optionsymbol.strike))
                    option_payoff.append(float(100*i.contracts*(float(latest_stock) + float(i.buysellprice) - float(qs_options[0].optionsymbol.strike))))

        if i.optionsymbol.asset == 'FTSE':
            if i.position == 'Long':
                option_debit_credit.append(-float(2*i.contracts*i.buysellprice))
            else:
                option_debit_credit.append(float(2*i.contracts*i.buysellprice))
            option_valuation.append(float(2*i.contracts*latest_clos))
            option_delta.append(float(i.contracts*latest_delta))
            option_contracts.append(float(i.contracts))
        else:
            if i.position == 'Long':
                option_debit_credit.append(-float(100*i.contracts*i.buysellprice))
            else:
                option_debit_credit.append(float(100*i.contracts*i.buysellprice))
            option_valuation.append(float(100*i.contracts*latest_clos))      
            option_delta.append(float(i.contracts*latest_delta))
            option_contracts.append(float(i.contracts))       

    max_futures_dates, futures_clos_prices, futures_stock_prices, fixing_prices, futures_profits, future_debit_credit, future_valuation, future_payoff, future_contracts = ([] for i in range(9))

    for i in active_futures:
        qs_futures = Future.objects.filter(futuresymbol=PortfolioFuture.objects.get(id=i.id).futuresymbol.id)
        max_futures_date = qs_futures.aggregate(Max('date'))

        max_futures_dates.append(max_futures_date['date__max'].strftime("%#d/%#m/%Y"))

        latest_clos = qs_futures.filter(date=max_futures_date['date__max']).values('closing_price')[0]['closing_price']
        futures_clos_prices.append(json.dumps(latest_clos, cls=DecimalEncoder))

        latest_stock = qs_futures.filter(date=max_futures_date['date__max']).values('stock')[0]['stock']
        futures_stock_prices.append(json.dumps(latest_stock, cls=DecimalEncoder))

        latest_fixing_price = qs_futures.filter(date=max_futures_date['date__max']).values('fixing_price')[0]['fixing_price']
        fixing_prices.append(json.dumps(latest_fixing_price, cls=DecimalEncoder))

        if i.futuresymbol.asset == 'FTSE':
            if i.position == 'Long':
                if latest_fixing_price > 0:
                    futures_profits.append(float(latest_fixing_price) - float(i.buysellprice))
                    future_payoff.append(float(2*i.contracts*(float(latest_fixing_price) - float(i.buysellprice))))
                else:
                    futures_profits.append(float(latest_clos) - float(i.buysellprice))
                    future_payoff.append(float(2*i.contracts*(float(latest_clos) - float(i.buysellprice))))

            if i.position == 'Short':
                if latest_fixing_price > 0:
                    futures_profits.append(float(i.buysellprice) - float(latest_fixing_price))
                    future_payoff.append(float(2*i.contracts*(float(i.buysellprice) - float(latest_fixing_price))))
                else:
                    futures_profits.append(float(i.buysellprice) - float(latest_clos))
                    future_payoff.append(float(2*i.contracts*(float(i.buysellprice) - float(latest_clos))))
                    
        else:
            if i.position == 'Long':
                if latest_fixing_price > 0:
                    futures_profits.append(float(latest_fixing_price) - float(i.buysellprice))
                    future_payoff.append(float(100*i.contracts*(float(latest_fixing_price) - float(i.buysellprice))))
                else:
                    futures_profits.append(float(latest_clos) - float(i.buysellprice))
                    future_payoff.append(float(100*i.contracts*(float(latest_clos) - float(i.buysellprice))))

            if i.position == 'Short':
                if latest_fixing_price > 0:
                    futures_profits.append(float(i.buysellprice) - float(latest_fixing_price))
                    future_payoff.append(float(100*i.contracts*(float(i.buysellprice) - float(latest_fixing_price))))
                else:
                    futures_profits.append(float(i.buysellprice) - float(latest_clos))
                    future_payoff.append(float(100*i.contracts*(float(i.buysellprice) - float(latest_clos))))

        if i.futuresymbol.asset == 'FTSE':
            if i.position == 'Long':
                future_debit_credit.append(-float(2*i.contracts*i.buysellprice))
            else:
                future_debit_credit.append(float(2*i.contracts*i.buysellprice))
            future_valuation.append(float(2*i.contracts*latest_clos))
            future_contracts.append(float(i.contracts))
        else:
            if i.position == 'Long':
                future_debit_credit.append(-float(100*i.contracts*i.buysellprice))
            else:
                future_debit_credit.append(float(100*i.contracts*i.buysellprice))
            future_valuation.append(float(100*i.contracts*latest_clos)) 
            future_contracts.append(float(i.contracts))

    max_stocks_dates, stock_stock_prices, stock_debit_credit, stocks_profits, stocks_valuation, stocks_total_payoff, stocks_quantity = ([] for i in range(7))

    for i in stocks:
        qs_stocks = Stock.objects.filter(stocksymbol=PortfolioStock.objects.get(id=i.id).stocksymbol.id)
        max_stocks_date = qs_stocks.aggregate(Max('date'))
        
        max_stocks_dates.append(max_stocks_date['date__max'].strftime("%#d/%#m/%Y"))
        
        latest_stock = qs_stocks.filter(date=max_stocks_date['date__max']).values('close')[0]['close']
        stock_stock_prices.append(json.dumps(latest_stock, cls=DecimalEncoder))
        stock_debit_credit.append(float(i.quantity*float(i.buyprice)))
        stocks_quantity.append(float(i.quantity))
        
        stocks_profits.append(float(latest_stock)-float(i.buyprice))
        stocks_valuation.append(float(i.quantity*latest_stock))
        stocks_total_payoff.append(float(i.quantity*(float(latest_stock)-float(i.buyprice))))

    if request.method == "POST":
        portfolioFutureForm = PortfolioFutureForm(request.POST)
        if portfolioFutureForm.is_valid():
            asset_fut = request.POST.get('asset')
            expmonth_fut = request.POST.get('exp_month')
            expyear_fut = request.POST.get('exp_year')
            try:
                qs = Futuresymbol.objects.filter(expmonthdate__gte=date.today()).filter(asset=asset_fut).filter(expmonthdate__month=expmonth_fut).filter(expmonthdate__year=expyear_fut)
                futuresymbol_ = qs[0]
                portfolioFuture = PortfolioFuture(
                    futuresymbol = futuresymbol_,
                    position = portfolioFutureForm.cleaned_data["position_type"],
                    contracts = portfolioFutureForm.cleaned_data["contracts"],
                    buysellprice = portfolioFutureForm.cleaned_data["buysellprice"],
                )
                
                portfolioFuture.save()
                portfolioFuture.portfolio.add(portfolio)
       
            except (IndexError, Futuresymbol.DoesNotExist):
                return render(request, 'accounts/myportfolio-detail.html', {
                    'portfolio': portfolio,
                    'options': options,
                    'futures': futures,
                    'stocks': stocks,
                    'active_options': active_options,
                    'active_options_count': len(active_options),
                    'active_futures': active_futures,
                    'active_futures_count': len(active_futures),
                    'portfolioFutureForm': portfolioFutureForm,
                    'max_options_dates': max_options_dates,   
                    'options_clos_prices': options_clos_prices,     
                    'stock_prices': stock_prices,       
                    'profits': profits,
                    'option_debit_credit': option_debit_credit,
                    'option_valuation': option_valuation,
                    'option_payoff': option_payoff,    
                    'option_delta': option_delta,
                    'max_futures_dates': max_futures_dates, 
                    'futures_clos_prices': futures_clos_prices,
                    'futures_stock_prices': futures_stock_prices,
                    'fixing_prices': fixing_prices,
                    'futures_profits': futures_profits,
                    'future_debit_credit': future_debit_credit,
                    'future_valuation': future_valuation,
                    'future_payoff': future_payoff,
                    'max_stocks_dates': max_stocks_dates,
                    'stock_stock_prices': stock_stock_prices,
                    'stock_debit_credit':stock_debit_credit,
                    'stocks_profits': stocks_profits,
                    'stocks_valuation': stocks_valuation,
                    'stocks_total_payoff': stocks_total_payoff,
                    'stocks_count': len(stocks),
                    'stocks_quantity': sum(stocks_quantity),
                    'total_portfolio_valuation': sum(option_valuation)+sum(future_valuation)+sum(stocks_valuation),
                    'total_portfolio_payoff': sum(option_payoff)+sum(future_payoff)+sum(stocks_total_payoff),
                    'total_option_contracts': sum(option_contracts),
                    'total_option_debit_credit': sum(option_debit_credit),
                    'total_option_valuation': sum(option_valuation),
                    'total_option_payoff': sum(option_payoff),
                    'total_option_delta': sum(option_delta),
                    'total_future_contracts': sum(future_contracts),
                    'total_future_debit_credit': sum(future_debit_credit),
                    'total_future_valuation': sum(future_valuation),
                    'total_future_payoff': sum(future_payoff),
                    'total_stock_debit_credit': sum(stock_debit_credit),
                    'total_stock_valuation': sum(stocks_valuation),
                    'total_stock_payoff': sum(stocks_total_payoff),
                    'today': date.today(),
                    'error_future_message': 'Please select a valid not expired future',
                    })

            else:
                return HttpResponseRedirect(request.path_info)

    context = {'portfolio': portfolio,
                'options': options,
                'futures': futures,
                'stocks': stocks,
                'active_options': active_options,
                'active_options_count': len(active_options),
                'active_futures': active_futures,
                'active_futures_count': len(active_futures),
                'portfolioOptionForm': portfolioOptionForm,
                'portfolioFutureForm': portfolioFutureForm,
                'portfolioStockForm': portfolioStockForm,
                'max_options_dates': max_options_dates,
                'options_clos_prices': options_clos_prices,
                'stock_prices': stock_prices,
                'profits': profits,
                'option_debit_credit': option_debit_credit,
                'option_valuation': option_valuation,
                'option_payoff': option_payoff,
                'option_delta': option_delta,
                'max_futures_dates': max_futures_dates, 
                'futures_clos_prices': futures_clos_prices,
                'futures_stock_prices': futures_stock_prices,
                'fixing_prices': fixing_prices,
                'futures_profits': futures_profits,
                'future_debit_credit': future_debit_credit,
                'future_valuation': future_valuation,
                'future_payoff': future_payoff,
                'max_stocks_dates': max_stocks_dates,
                'stock_stock_prices': stock_stock_prices,
                'stock_debit_credit':stock_debit_credit,
                'stocks_profits': stocks_profits,
                'stocks_valuation': stocks_valuation,
                'stocks_total_payoff': stocks_total_payoff,
                'stocks_count': len(stocks),
                'stocks_quantity': sum(stocks_quantity),
                'total_portfolio_valuation': sum(option_valuation)+sum(future_valuation)+sum(stocks_valuation),
                'total_portfolio_payoff': sum(option_payoff)+sum(future_payoff)+sum(stocks_total_payoff),
                'total_option_contracts': sum(option_contracts),
                'total_option_debit_credit': sum(option_debit_credit),
                'total_option_valuation': sum(option_valuation),
                'total_option_payoff': sum(option_payoff),
                'total_option_delta': sum(option_delta),
                'total_future_contracts': sum(future_contracts),
                'total_future_debit_credit': sum(future_debit_credit),
                'total_future_valuation': sum(future_valuation),
                'total_future_payoff': sum(future_payoff),
                'total_stock_debit_credit': sum(stock_debit_credit),
                'total_stock_valuation': sum(stocks_valuation),
                'total_stock_payoff': sum(stocks_total_payoff),
                'today': date.today(),
                }

    return render(request, 'accounts/myportfolio-detail.html', context)
    #return redirect(reverse('accounts:portfolio-detail', kwargs={ 'portfolio_id': portfolio_id, }))

@ login_required
def PortfolioStockDetailView(request, portfolio_id):

    portfolio = Portfolio.objects.get(pk=portfolio_id)
    options = PortfolioOption.objects.filter(portfolio=portfolio_id)
    futures = PortfolioFuture.objects.filter(portfolio=portfolio_id)
    stocks = PortfolioStock.objects.filter(portfolio=portfolio_id)
    portfolioOptionForm = PortfolioOptionForm()
    portfolioFutureForm = PortfolioFutureForm()
    portfolioStockForm = PortfolioStockForm()

    active_options=[]
    for i in range(len(options)):
        if options[i].active_option():
            active_options.append(options[i])

    active_futures=[]
    for i in range(len(futures)):
        if futures[i].active_future():
            active_futures.append(futures[i])

    max_options_dates, options_clos_prices, stock_prices, profits, option_debit_credit, option_valuation, option_payoff, option_delta, option_contracts = ([] for i in range(9))

    for i in active_options:
        qs_options = Option.objects.filter(optionsymbol=PortfolioOption.objects.get(id=i.id).optionsymbol.id)
        max_options_date = qs_options.aggregate(Max('date'))
        option_strike = json.dumps(qs_options[0].optionsymbol.strike, cls=DecimalEncoder)
        option_type = qs_options[0].optionsymbol.optiontype

        max_options_dates.append(max_options_date['date__max'].strftime("%#d/%#m/%Y"))

        latest_clos = qs_options.filter(date=max_options_date['date__max']).values('closing_price')[0]['closing_price']
        options_clos_prices.append(json.dumps(latest_clos, cls=DecimalEncoder))

        latest_stock = qs_options.filter(date=max_options_date['date__max']).values('stock')[0]['stock']
        stock_prices.append(json.dumps(latest_stock, cls=DecimalEncoder))

        latest_delta = qs_options.filter(date=max_options_date['date__max']).values('delta')[0]['delta']
        #option_delta.append(json.dumps(latest_delta, cls=DecimalEncoder)) 

        if i.optionsymbol.asset == 'FTSE':
            if option_type == 'c':
                if i.position == 'Long':
                    profits.append(float(latest_stock) - float(qs_options[0].optionsymbol.strike) - float(i.buysellprice))
                    option_payoff.append(float(2*i.contracts*(float(latest_stock) - float(qs_options[0].optionsymbol.strike) - float(i.buysellprice))))
                else:
                    profits.append(float(qs_options[0].optionsymbol.strike) + float(i.buysellprice) - float(latest_stock))
                    option_payoff.append(float(2*i.contracts*(float(qs_options[0].optionsymbol.strike) + float(i.buysellprice) - float(latest_stock))))

            if option_type == 'p':
                if i.position == 'Long':                
                    profits.append(float(qs_options[0].optionsymbol.strike) - float(latest_stock) - float(i.buysellprice))
                    option_payoff.append(float(2*i.contracts*(float(qs_options[0].optionsymbol.strike) - float(latest_stock) - float(i.buysellprice))))
                else:
                    profits.append(float(latest_stock) + float(i.buysellprice) - float(qs_options[0].optionsymbol.strike))
                    option_payoff.append(float(2*i.contracts*(float(latest_stock) + float(i.buysellprice) - float(qs_options[0].optionsymbol.strike))))

        else:
            if option_type == 'c':
                if i.position == 'Long':
                    profits.append(float(latest_stock) - float(qs_options[0].optionsymbol.strike) - float(i.buysellprice))
                    option_payoff.append(float(100*i.contracts*(float(latest_stock) - float(qs_options[0].optionsymbol.strike) - float(i.buysellprice))))
                else:
                    profits.append(float(qs_options[0].optionsymbol.strike) + float(i.buysellprice) - float(latest_stock))
                    option_payoff.append(float(100*i.contracts*(float(qs_options[0].optionsymbol.strike) + float(i.buysellprice) - float(latest_stock))))
                    

            if option_type == 'p':
                if i.position == 'Long':                
                    profits.append(float(qs_options[0].optionsymbol.strike) - float(latest_stock) - float(i.buysellprice))
                    option_payoff.append(float(100*i.contracts*(float(qs_options[0].optionsymbol.strike) - float(latest_stock) - float(i.buysellprice))))
                else:
                    profits.append(float(latest_stock) + float(i.buysellprice) - float(qs_options[0].optionsymbol.strike))
                    option_payoff.append(float(100*i.contracts*(float(latest_stock) + float(i.buysellprice) - float(qs_options[0].optionsymbol.strike))))

        if i.optionsymbol.asset == 'FTSE':
            if i.position == 'Long':
                option_debit_credit.append(-float(2*i.contracts*i.buysellprice))
            else:
                option_debit_credit.append(float(2*i.contracts*i.buysellprice))
            option_valuation.append(float(2*i.contracts*latest_clos))
            option_delta.append(float(i.contracts*latest_delta))
            option_contracts.append(float(i.contracts))
        else:
            if i.position == 'Long':
                option_debit_credit.append(-float(100*i.contracts*i.buysellprice))
            else:
                option_debit_credit.append(float(100*i.contracts*i.buysellprice))
            option_valuation.append(float(100*i.contracts*latest_clos))      
            option_delta.append(float(i.contracts*latest_delta))
            option_contracts.append(float(i.contracts))    

    max_futures_dates, futures_clos_prices, futures_stock_prices, fixing_prices, futures_profits, future_debit_credit, future_valuation, future_payoff, future_contracts = ([] for i in range(9))

    for i in active_futures:
        qs_futures = Future.objects.filter(futuresymbol=PortfolioFuture.objects.get(id=i.id).futuresymbol.id)
        max_futures_date = qs_futures.aggregate(Max('date'))

        max_futures_dates.append(max_futures_date['date__max'].strftime("%#d/%#m/%Y"))

        latest_clos = qs_futures.filter(date=max_futures_date['date__max']).values('closing_price')[0]['closing_price']
        futures_clos_prices.append(json.dumps(latest_clos, cls=DecimalEncoder))

        latest_stock = qs_futures.filter(date=max_futures_date['date__max']).values('stock')[0]['stock']
        futures_stock_prices.append(json.dumps(latest_stock, cls=DecimalEncoder))

        latest_fixing_price = qs_futures.filter(date=max_futures_date['date__max']).values('fixing_price')[0]['fixing_price']
        fixing_prices.append(json.dumps(latest_fixing_price, cls=DecimalEncoder))

        if i.futuresymbol.asset == 'FTSE':
            if i.position == 'Long':
                if latest_fixing_price > 0:
                    futures_profits.append(float(latest_fixing_price) - float(i.buysellprice))
                    future_payoff.append(float(2*i.contracts*(float(latest_fixing_price) - float(i.buysellprice))))
                else:
                    futures_profits.append(float(latest_clos) - float(i.buysellprice))
                    future_payoff.append(float(2*i.contracts*(float(latest_clos) - float(i.buysellprice))))

            if i.position == 'Short':
                if latest_fixing_price > 0:
                    futures_profits.append(float(i.buysellprice) - float(latest_fixing_price))
                    future_payoff.append(float(2*i.contracts*(float(i.buysellprice) - float(latest_fixing_price))))
                else:
                    futures_profits.append(float(i.buysellprice) - float(latest_clos))
                    future_payoff.append(float(2*i.contracts*(float(i.buysellprice) - float(latest_clos))))
                    
        else:
            if i.position == 'Long':
                if latest_fixing_price > 0:
                    futures_profits.append(float(latest_fixing_price) - float(i.buysellprice))
                    future_payoff.append(float(100*i.contracts*(float(latest_fixing_price) - float(i.buysellprice))))
                else:
                    futures_profits.append(float(latest_clos) - float(i.buysellprice))
                    future_payoff.append(float(100*i.contracts*(float(latest_clos) - float(i.buysellprice))))

            if i.position == 'Short':
                if latest_fixing_price > 0:
                    futures_profits.append(float(i.buysellprice) - float(latest_fixing_price))
                    future_payoff.append(float(100*i.contracts*(float(i.buysellprice) - float(latest_fixing_price))))
                else:
                    futures_profits.append(float(i.buysellprice) - float(latest_clos))
                    future_payoff.append(float(100*i.contracts*(float(i.buysellprice) - float(latest_clos))))

        if i.futuresymbol.asset == 'FTSE':
            if i.position == 'Long':
                future_debit_credit.append(-float(2*i.contracts*i.buysellprice))
            else:
                future_debit_credit.append(float(2*i.contracts*i.buysellprice))
            future_valuation.append(float(2*i.contracts*latest_clos))
            future_contracts.append(float(i.contracts))
        else:
            if i.position == 'Long':
                future_debit_credit.append(-float(100*i.contracts*i.buysellprice))
            else:
                future_debit_credit.append(float(100*i.contracts*i.buysellprice))
            future_valuation.append(float(100*i.contracts*latest_clos)) 
            future_contracts.append(float(i.contracts))

    max_stocks_dates, stock_stock_prices, stock_debit_credit, stocks_profits, stocks_valuation, stocks_total_payoff, stocks_quantity = ([] for i in range(7))

    for i in stocks:
        qs_stocks = Stock.objects.filter(stocksymbol=PortfolioStock.objects.get(id=i.id).stocksymbol.id)
        max_stocks_date = qs_stocks.aggregate(Max('date'))
        
        max_stocks_dates.append(max_stocks_date['date__max'].strftime("%#d/%#m/%Y"))
        
        latest_stock = qs_stocks.filter(date=max_stocks_date['date__max']).values('close')[0]['close']
        stock_stock_prices.append(json.dumps(latest_stock, cls=DecimalEncoder))
        stock_debit_credit.append(float(i.quantity*float(i.buyprice)))
        stocks_quantity.append(float(i.quantity))
        
        stocks_profits.append(float(latest_stock)-float(i.buyprice))
        stocks_valuation.append(float(i.quantity*latest_stock))
        stocks_total_payoff.append(float(i.quantity*(float(latest_stock)-float(i.buyprice))))

    if request.method == "POST":
        portfolioStockForm = PortfolioStockForm(request.POST)
        if portfolioStockForm.is_valid():
            asset_stock = request.POST.get('asset')
            try:
                qs = Stocksymbol.objects.filter(asset=asset_stock)
                stocksymbol_ = qs[0]
                portfolioStock = PortfolioStock(
                    stocksymbol = stocksymbol_,
                    quantity = portfolioStockForm.cleaned_data["quantity"],
                    buyprice = portfolioStockForm.cleaned_data["buyprice"],
                )
                
                portfolioStock.save()
                portfolioStock.portfolio.add(portfolio)

            except (IndexError, Stocksymbol.DoesNotExist):
                return render(request, 'accounts/myportfolio-detail.html', {
                    'portfolio': portfolio,
                    'options': options,
                    'futures': futures,
                    'stocks': stocks,
                    'active_options': active_options,
                    'active_options_count': len(active_options),
                    'active_futures': active_futures,
                    'active_futures_count': len(active_futures),
                    'portfolioOptionForm': portfolioOptionForm,
                    'portfolioFutureForm': portfolioFutureForm,
                    'portfolioStockForm': portfolioStockForm,
                    'max_options_dates': max_options_dates,   
                    'options_clos_prices': options_clos_prices,     
                    'stock_prices': stock_prices,       
                    'profits': profits,    
                    'option_debit_credit': option_debit_credit,
                    'option_valuation': option_valuation,
                    'option_payoff': option_payoff,
                    'option_delta': option_delta,
                    'max_futures_dates': max_futures_dates, 
                    'futures_clos_prices': futures_clos_prices,
                    'futures_stock_prices': futures_stock_prices,
                    'fixing_prices': fixing_prices,
                    'futures_profits': futures_profits,
                    'future_debit_credit': future_debit_credit,
                    'future_valuation': future_valuation,
                    'future_payoff': future_payoff,
                    'max_stocks_dates': max_stocks_dates,
                    'stock_stock_prices': stock_stock_prices,
                    'stock_debit_credit':stock_debit_credit,
                    'stocks_profits': stocks_profits,
                    'stocks_valuation': stocks_valuation,
                    'stocks_total_payoff': stocks_total_payoff,
                    'stocks_count': len(stocks),
                    'stocks_quantity': sum(stocks_quantity),
                    'total_portfolio_valuation': sum(option_valuation)+sum(future_valuation)+sum(stocks_valuation),
                    'total_portfolio_payoff': sum(option_payoff)+sum(future_payoff)+sum(stocks_total_payoff),
                    'total_option_contracts': sum(option_contracts),
                    'total_option_debit_credit': sum(option_debit_credit),
                    'total_option_valuation': sum(option_valuation),
                    'total_option_payoff': sum(option_payoff),
                    'total_option_delta': sum(option_delta),
                    'total_future_contracts': sum(future_contracts),
                    'total_future_debit_credit': sum(future_debit_credit),
                    'total_future_valuation': sum(future_valuation),
                    'total_future_payoff': sum(future_payoff),
                    'total_stock_debit_credit': sum(stock_debit_credit),
                    'total_stock_valuation': sum(stocks_valuation),
                    'total_stock_payoff': sum(stocks_total_payoff),
                    'today': date.today(),
                    'error_stock_message': 'Please select a valid stock',
                    })

            else:
                return HttpResponseRedirect(request.path_info)

    context = {'portfolio': portfolio,
                'options': options,
                'futures': futures,
                'stocks': stocks,
                'active_options': active_options,
                'active_options_count': len(active_options),
                'active_futures': active_futures,
                'active_futures_count': len(active_futures),
                'portfolioOptionForm': portfolioOptionForm,
                'portfolioFutureForm': portfolioFutureForm,
                'portfolioStockForm': portfolioStockForm,
                'max_options_dates': max_options_dates,
                'options_clos_prices': options_clos_prices,
                'stock_prices': stock_prices,
                'profits': profits,
                'option_debit_credit': option_debit_credit,
                'option_valuation': option_valuation,
                'option_payoff': option_payoff,
                'option_delta': option_delta,
                'max_futures_dates': max_futures_dates, 
                'futures_clos_prices': futures_clos_prices,
                'futures_stock_prices': futures_stock_prices,
                'fixing_prices': fixing_prices,
                'futures_profits': futures_profits,
                'future_debit_credit': option_debit_credit,
                'future_valuation': option_valuation,
                'future_payoff': option_payoff,
                'max_stocks_dates': max_stocks_dates,
                'stock_stock_prices': stock_stock_prices,
                'stock_debit_credit':stock_debit_credit,
                'stocks_profits': stocks_profits,
                'stocks_valuation': stocks_valuation,
                'stocks_total_payoff': stocks_total_payoff,
                'stocks_count': len(stocks),
                'stocks_quantity': sum(stocks_quantity),
                'total_portfolio_valuation': sum(option_valuation)+sum(future_valuation)+sum(stocks_valuation),
                'total_portfolio_payoff': sum(option_payoff)+sum(future_payoff)+sum(stocks_total_payoff),
                'total_option_contracts': sum(option_contracts),
                'total_option_debit_credit': sum(option_debit_credit),
                'total_option_valuation': sum(option_valuation),
                'total_option_payoff': sum(option_payoff),
                'total_option_delta': sum(option_delta),
                'total_future_contracts': sum(future_contracts),
                'total_future_debit_credit': sum(future_debit_credit),
                'total_future_valuation': sum(future_valuation),
                'total_future_payoff': sum(future_payoff),
                'total_stock_debit_credit': sum(stock_debit_credit),
                'total_stock_valuation': sum(stocks_valuation),
                'total_stock_payoff': sum(stocks_total_payoff),
                'today': date.today(),
                }

    return render(request, 'accounts/myportfolio-detail.html', context)

@ login_required
def DeletePortfolioStockView(request):
    if request.method == "POST":
        portfoliostock_ids = request.POST.getlist('id[]')
        portfolio_id = request.POST.get('portfolio_id')
        for id in portfoliostock_ids:
            portfoliostock = PortfolioStock.objects.get(pk=id)
            portfoliostock.delete()
        return redirect(reverse('accounts:portfolio-detail', kwargs={ 'portfolio_id': portfolio_id, }))

@ login_required
def UpdatePortfolioStockView(request, portfolio_id, portfoliostock_id):
    portfoliostock = PortfolioStock.objects.get(pk=portfoliostock_id)
    asset = portfoliostock.stocksymbol.get_asset_display()
    portfolioStockUpdateForm = PortfolioStockUpdateModelForm(instance=portfoliostock)

    if request.method == 'POST':
        portfolioStockUpdateForm = PortfolioStockUpdateModelForm(request.POST, instance=portfoliostock)
        if portfolioStockUpdateForm.is_valid():
            portfolioStockUpdateForm.save()
        return redirect(reverse('accounts:portfolio-detail', kwargs={ 'portfolio_id': portfolio_id, }))

    return render(request, 'accounts/myportfoliostock-update.html', {'portfoliostock':portfoliostock, 'portfolioStockUpdateForm': portfolioStockUpdateForm, 'asset':asset,})

@ login_required
def PortfolioValuationView(request, portfolio_id):
    portfolio = Portfolio.objects.get(pk=portfolio_id)
    active_options=PortfolioOption.objects.filter(portfolio=portfolio_id).filter(optionsymbol__expmonthdate__gte=date.today())
    active_futures=PortfolioFuture.objects.filter(portfolio=portfolio_id).filter(futuresymbol__expmonthdate__gte=date.today())
    stocks = PortfolioStock.objects.filter(portfolio=portfolio_id)

    option_valuation, future_valuation, stock_valuation, option_names, future_names, stock_names = ([] for i in range(6)) 

    for i in active_options:
        qs_options = Option.objects.filter(optionsymbol=PortfolioOption.objects.get(id=i.id).optionsymbol.id)
        max_options_date = qs_options.aggregate(Max('date'))
        latest_clos = qs_options.filter(date=max_options_date['date__max']).values('closing_price')[0]['closing_price']
        if i.optionsymbol.asset == 'FTSE':
            option_valuation.append(float(2*i.contracts*latest_clos))
            option_names.append(i.optionsymbol.symbol)
        else:
            option_valuation.append(float(100*i.contracts*latest_clos))
            option_names.append(i.optionsymbol.symbol)
        
    for i in active_futures:
        qs_futures = Future.objects.filter(futuresymbol=PortfolioFuture.objects.get(id=i.id).futuresymbol.id)
        max_futures_date = qs_futures.aggregate(Max('date'))
        latest_clos = qs_futures.filter(date=max_futures_date['date__max']).values('closing_price')[0]['closing_price']
        if i.futuresymbol.asset == 'FTSE':
            future_valuation.append(float(2*i.contracts*latest_clos))
            future_names.append(i.futuresymbol.symbol)
        else:
            future_valuation.append(float(100*i.contracts*latest_clos))
            future_names.append(i.futuresymbol.symbol)

    for i in stocks:
        qs_stocks = Stock.objects.filter(stocksymbol=PortfolioStock.objects.get(id=i.id).stocksymbol.id)
        max_stocks_date = qs_stocks.aggregate(Max('date'))
        latest_stock = qs_stocks.filter(date=max_stocks_date['date__max']).values('close')[0]['close']
        stock_valuation.append(float(i.quantity*latest_stock))
        stock_names.append(i.stocksymbol.get_asset_display())

    option_valuation.extend(future_valuation)
    option_valuation.extend(stock_valuation)
    option_names.extend(future_names)
    option_names.extend(stock_names)

    portfolio_valuations=[]
    for i in range(len(option_names)):
        portfolio_valuations.append({option_names[i]:option_valuation[i]})

    return JsonResponse(portfolio_valuations, safe=False)

def render_pdf_view(request):
    template_path = 'accounts/pdf_test.html'
    context = {'myvar': 'this is your template context'}
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    # if download:
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    # if display:
    #response['Content-Disposition'] = 'filename="report.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response)
    # if error then show some funy view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

def PortfolioValuationPDFView(request, portfolio_id):

    portfolio = Portfolio.objects.get(pk=portfolio_id)
    options = PortfolioOption.objects.filter(portfolio=portfolio_id)
    futures = PortfolioFuture.objects.filter(portfolio=portfolio_id)
    stocks = PortfolioStock.objects.filter(portfolio=portfolio_id)

    active_options=[]
    for i in range(len(options)):
        if options[i].active_option():
            active_options.append(options[i])

    active_futures=[]
    for i in range(len(futures)):
        if futures[i].active_future():
            active_futures.append(futures[i])

    max_options_dates, options_clos_prices, stock_prices, profits, option_debit_credit, option_valuation, option_payoff, option_delta, option_contracts = ([] for i in range(9))

    for i in active_options:
        qs_options = Option.objects.filter(optionsymbol=PortfolioOption.objects.get(id=i.id).optionsymbol.id)
        max_options_date = qs_options.aggregate(Max('date'))
        option_strike = json.dumps(qs_options[0].optionsymbol.strike, cls=DecimalEncoder)
        option_type = qs_options[0].optionsymbol.optiontype

        max_options_dates.append(max_options_date['date__max'].strftime("%#d/%#m/%Y"))

        latest_clos = qs_options.filter(date=max_options_date['date__max']).values('closing_price')[0]['closing_price']
        options_clos_prices.append(json.dumps(latest_clos, cls=DecimalEncoder))

        latest_stock = qs_options.filter(date=max_options_date['date__max']).values('stock')[0]['stock']
        stock_prices.append(json.dumps(latest_stock, cls=DecimalEncoder))

        latest_delta = qs_options.filter(date=max_options_date['date__max']).values('delta')[0]['delta']
        #option_delta.append(json.dumps(latest_delta, cls=DecimalEncoder)) 

        if i.optionsymbol.asset == 'FTSE':
            if option_type == 'c':
                if i.position == 'Long':
                    profits.append(float(latest_stock) - float(qs_options[0].optionsymbol.strike) - float(i.buysellprice))
                    option_payoff.append(float(2*i.contracts*(float(latest_stock) - float(qs_options[0].optionsymbol.strike) - float(i.buysellprice))))
                else:
                    profits.append(float(qs_options[0].optionsymbol.strike) + float(i.buysellprice) - float(latest_stock))
                    option_payoff.append(float(2*i.contracts*(float(qs_options[0].optionsymbol.strike) + float(i.buysellprice) - float(latest_stock))))

            if option_type == 'p':
                if i.position == 'Long':                
                    profits.append(float(qs_options[0].optionsymbol.strike) - float(latest_stock) - float(i.buysellprice))
                    option_payoff.append(float(2*i.contracts*(float(qs_options[0].optionsymbol.strike) - float(latest_stock) - float(i.buysellprice))))
                else:
                    profits.append(float(latest_stock) + float(i.buysellprice) - float(qs_options[0].optionsymbol.strike))
                    option_payoff.append(float(2*i.contracts*(float(latest_stock) + float(i.buysellprice) - float(qs_options[0].optionsymbol.strike))))

        else:
            if option_type == 'c':
                if i.position == 'Long':
                    profits.append(float(latest_stock) - float(qs_options[0].optionsymbol.strike) - float(i.buysellprice))
                    option_payoff.append(float(100*i.contracts*(float(latest_stock) - float(qs_options[0].optionsymbol.strike) - float(i.buysellprice))))
                else:
                    profits.append(float(qs_options[0].optionsymbol.strike) + float(i.buysellprice) - float(latest_stock))
                    option_payoff.append(float(100*i.contracts*(float(qs_options[0].optionsymbol.strike) + float(i.buysellprice) - float(latest_stock))))
                    

            if option_type == 'p':
                if i.position == 'Long':                
                    profits.append(float(qs_options[0].optionsymbol.strike) - float(latest_stock) - float(i.buysellprice))
                    option_payoff.append(float(100*i.contracts*(float(qs_options[0].optionsymbol.strike) - float(latest_stock) - float(i.buysellprice))))
                else:
                    profits.append(float(latest_stock) + float(i.buysellprice) - float(qs_options[0].optionsymbol.strike))
                    option_payoff.append(float(100*i.contracts*(float(latest_stock) + float(i.buysellprice) - float(qs_options[0].optionsymbol.strike))))

        if i.optionsymbol.asset == 'FTSE':
            if i.position == 'Long':
                option_debit_credit.append(-float(2*i.contracts*i.buysellprice))
            else:
                option_debit_credit.append(float(2*i.contracts*i.buysellprice))
            option_valuation.append(float(2*i.contracts*latest_clos))
            option_delta.append(float(i.contracts*latest_delta))
            option_contracts.append(float(i.contracts))
        else:
            if i.position == 'Long':
                option_debit_credit.append(-float(100*i.contracts*i.buysellprice))
            else:
                option_debit_credit.append(float(100*i.contracts*i.buysellprice))
            option_valuation.append(float(100*i.contracts*latest_clos))      
            option_delta.append(float(i.contracts*latest_delta))
            option_contracts.append(float(i.contracts))    

    max_futures_dates, futures_clos_prices, futures_stock_prices, fixing_prices, futures_profits, future_debit_credit, future_valuation, future_payoff, future_contracts = ([] for i in range(9))

    for i in active_futures:
        qs_futures = Future.objects.filter(futuresymbol=PortfolioFuture.objects.get(id=i.id).futuresymbol.id)
        max_futures_date = qs_futures.aggregate(Max('date'))

        max_futures_dates.append(max_futures_date['date__max'].strftime("%#d/%#m/%Y"))

        latest_clos = qs_futures.filter(date=max_futures_date['date__max']).values('closing_price')[0]['closing_price']
        futures_clos_prices.append(json.dumps(latest_clos, cls=DecimalEncoder))

        latest_stock = qs_futures.filter(date=max_futures_date['date__max']).values('stock')[0]['stock']
        futures_stock_prices.append(json.dumps(latest_stock, cls=DecimalEncoder))

        latest_fixing_price = qs_futures.filter(date=max_futures_date['date__max']).values('fixing_price')[0]['fixing_price']
        fixing_prices.append(json.dumps(latest_fixing_price, cls=DecimalEncoder))

        if i.futuresymbol.asset == 'FTSE':
            if i.position == 'Long':
                if latest_fixing_price > 0:
                    futures_profits.append(float(latest_fixing_price) - float(i.buysellprice))
                    future_payoff.append(float(2*i.contracts*(float(latest_fixing_price) - float(i.buysellprice))))
                else:
                    futures_profits.append(float(latest_clos) - float(i.buysellprice))
                    future_payoff.append(float(2*i.contracts*(float(latest_clos) - float(i.buysellprice))))

            if i.position == 'Short':
                if latest_fixing_price > 0:
                    futures_profits.append(float(i.buysellprice) - float(latest_fixing_price))
                    future_payoff.append(float(2*i.contracts*(float(i.buysellprice) - float(latest_fixing_price))))
                else:
                    futures_profits.append(float(i.buysellprice) - float(latest_clos))
                    future_payoff.append(float(2*i.contracts*(float(i.buysellprice) - float(latest_clos))))
                    
        else:
            if i.position == 'Long':
                if latest_fixing_price > 0:
                    futures_profits.append(float(latest_fixing_price) - float(i.buysellprice))
                    future_payoff.append(float(100*i.contracts*(float(latest_fixing_price) - float(i.buysellprice))))
                else:
                    futures_profits.append(float(latest_clos) - float(i.buysellprice))
                    future_payoff.append(float(100*i.contracts*(float(latest_clos) - float(i.buysellprice))))

            if i.position == 'Short':
                if latest_fixing_price > 0:
                    futures_profits.append(float(i.buysellprice) - float(latest_fixing_price))
                    future_payoff.append(float(100*i.contracts*(float(i.buysellprice) - float(latest_fixing_price))))
                else:
                    futures_profits.append(float(i.buysellprice) - float(latest_clos))
                    future_payoff.append(float(100*i.contracts*(float(i.buysellprice) - float(latest_clos))))

        if i.futuresymbol.asset == 'FTSE':
            if i.position == 'Long':
                future_debit_credit.append(-float(2*i.contracts*i.buysellprice))
            else:
                future_debit_credit.append(float(2*i.contracts*i.buysellprice))
            future_valuation.append(float(2*i.contracts*latest_clos))
            future_contracts.append(float(i.contracts))
        else:
            if i.position == 'Long':
                future_debit_credit.append(-float(100*i.contracts*i.buysellprice))
            else:
                future_debit_credit.append(float(100*i.contracts*i.buysellprice))
            future_valuation.append(float(100*i.contracts*latest_clos)) 
            future_contracts.append(float(i.contracts))

    max_stocks_dates, stock_stock_prices, stock_debit_credit, stocks_profits, stocks_valuation, stocks_total_payoff, stocks_quantity = ([] for i in range(7))

    for i in stocks:
        qs_stocks = Stock.objects.filter(stocksymbol=PortfolioStock.objects.get(id=i.id).stocksymbol.id)
        max_stocks_date = qs_stocks.aggregate(Max('date'))
        
        max_stocks_dates.append(max_stocks_date['date__max'].strftime("%#d/%#m/%Y"))
        
        latest_stock = qs_stocks.filter(date=max_stocks_date['date__max']).values('close')[0]['close']
        stock_stock_prices.append(json.dumps(latest_stock, cls=DecimalEncoder))
        stock_debit_credit.append(float(i.quantity*float(i.buyprice)))
        stocks_quantity.append(float(i.quantity))
        
        stocks_profits.append(float(latest_stock)-float(i.buyprice))
        stocks_valuation.append(float(i.quantity*latest_stock))
        stocks_total_payoff.append(float(i.quantity*(float(latest_stock)-float(i.buyprice))))

    context = {'portfolio': portfolio,
                'options': options,
                'futures': futures,
                'stocks': stocks,
                'active_options': active_options,
                'active_options_count': len(active_options),
                'active_futures': active_futures,
                'active_futures_count': len(active_futures),
                'max_options_dates': max_options_dates,
                'options_clos_prices': options_clos_prices,
                'stock_prices': stock_prices,
                'profits': profits,
                'option_debit_credit': option_debit_credit,
                'option_valuation': option_valuation,
                'option_payoff': option_payoff,
                'option_delta': option_delta,
                'max_futures_dates': max_futures_dates, 
                'futures_clos_prices': futures_clos_prices,
                'futures_stock_prices': futures_stock_prices,
                'fixing_prices': fixing_prices,
                'futures_profits': futures_profits,
                'future_debit_credit': option_debit_credit,
                'future_valuation': option_valuation,
                'future_payoff': option_payoff,
                'max_stocks_dates': max_stocks_dates,
                'stock_stock_prices': stock_stock_prices,
                'stock_debit_credit':stock_debit_credit,
                'stocks_profits': stocks_profits,
                'stocks_valuation': stocks_valuation,
                'stocks_total_payoff': stocks_total_payoff,
                'stocks_count': len(stocks),
                'stocks_quantity': sum(stocks_quantity),
                'total_portfolio_valuation': sum(option_valuation)+sum(future_valuation)+sum(stocks_valuation),
                'total_portfolio_payoff': sum(option_payoff)+sum(future_payoff)+sum(stocks_total_payoff),
                'total_option_contracts': sum(option_contracts),
                'total_option_debit_credit': sum(option_debit_credit),
                'total_option_valuation': sum(option_valuation),
                'total_option_payoff': sum(option_payoff),
                'total_option_delta': sum(option_delta),
                'total_future_contracts': sum(future_contracts),
                'total_future_debit_credit': sum(future_debit_credit),
                'total_future_valuation': sum(future_valuation),
                'total_future_payoff': sum(future_payoff),
                'total_stock_debit_credit': sum(stock_debit_credit),
                'total_stock_valuation': sum(stocks_valuation),
                'total_stock_payoff': sum(stocks_total_payoff),
                'today': date.today(),
                }

    template_path = 'accounts/pdf_portfolio_valuation.html'
    #context = {'myvar': 'this is your template context'}
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    # if download:
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    # if display:
    #response['Content-Disposition'] = 'filename="report.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response)
    # if error then show some funy view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

""" def MyPortfolioPDFView(request):

    myportfolios = Portfolio.objects.filter(creator=request.user)

    portfolio_active_options_count=[]
    for i in range(len(myportfolios)):
        portfolio_active_options_count.append(myportfolios[i].active_option_count())

    portfolio_active_futures_count=[]
    for i in range(len(myportfolios)):
        portfolio_active_futures_count.append(myportfolios[i].active_future_count())

    portfolio_stocks_count=[]
    for i in range(len(myportfolios)):
        portfolio_stocks_count.append(myportfolios[i].stock_count())

    context = {'myportfolios': myportfolios,
                'portfolio_active_options_count': portfolio_active_options_count,
                'portfolio_active_futures_count': portfolio_active_futures_count,
                'portfolio_stocks_count': portfolio_stocks_count}

    template_path = 'accounts/pdf_portfolios.html'
    #context = {'myvar': 'this is your template context'}
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    # if download:
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    # if display:
    #response['Content-Disposition'] = 'filename="report.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response)
    # if error then show some funy view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response """

"""
@ login_required
def DashBoardView(request):
    myoptionlist = Optionsymbol.objects.filter(optionscreeners=request.user).order_by('asset', '-expmonthdate', 'optiontype', 'strike')
    myfuturelist = Futuresymbol.objects.filter(futurescreeners=request.user).order_by('asset', '-expmonthdate')
    myoptionlist_count = myoptionlist.count()
    myfuturelist_count = myfuturelist.count()

    opt_latest_trad_date, opt_closing_prices, opt_changes, opt_volumes, opt_trades, opt_open_interests = ([] for i in range(6))

    for i in myoptionlist:
        opt = Option.objects.filter(optionsymbol__symbol = i)
        max_date = opt.aggregate(Max('date'))
        queryset = opt.filter(date=max_date['date__max'])
        opt_latest_trad_date.append(queryset[0].date.strftime("%d-%m-%Y"))
        opt_closing_prices.append(queryset[0].closing_price)
        opt_changes.append(queryset[0].change)
        opt_volumes.append(queryset[0].volume)
        opt_trades.append(queryset[0].trades)
        opt_open_interests.append(queryset[0].open_interest)

    paginator = Paginator(myoptionlist, 10)
    page_number = request.GET.get('page', 1)
    option_page_obj = paginator.get_page(page_number)

    fut_latest_trad_date, fut_closing_prices, fut_changes, fut_volumes, fut_trades, fut_open_interests = ([] for i in range(6))

    for i in myfuturelist:
        fut = Future.objects.filter(futuresymbol__symbol = i)
        max_date = fut.aggregate(Max('date'))
        queryset = fut.filter(date=max_date['date__max'])
        fut_latest_trad_date.append(queryset[0].date.strftime("%d-%m-%Y"))
        fut_closing_prices.append(queryset[0].closing_price)
        fut_changes.append(queryset[0].change)
        fut_volumes.append(queryset[0].volume)
        fut_trades.append(queryset[0].trades)
        fut_open_interests.append(queryset[0].open_interest)

    future_paginator = Paginator(myfuturelist, 10)
    future_page_number = request.GET.get('fpage', 1)
    future_page_obj = future_paginator.get_page(future_page_number)

    context = {
        'option_page_obj': option_page_obj,
        'myoptionlist_count': myoptionlist_count,
        'opt_latest_trad_date': opt_latest_trad_date,
        'opt_closing_prices': opt_closing_prices,
        'opt_changes': opt_changes,
        'opt_volumes': opt_volumes,
        'opt_trades': opt_trades,
        'opt_open_interests': opt_open_interests,
        'future_page_obj': future_page_obj,
        'myfuturelist_count': myfuturelist_count,
        'fut_latest_trad_date': fut_latest_trad_date,
        'fut_closing_prices': fut_closing_prices,
        'fut_changes': fut_changes,
        'fut_volumes': fut_volumes,
        'fut_trades': fut_trades,
        'fut_open_interests': fut_open_interests,
    }

    return render(request, 'accounts/mydashboard.html', context)
"""

@ login_required
@ csrf_exempt
def RemoveOptionScreenerView(request):
    if request.method == "POST":
        option_ids = request.POST.getlist('id[]')
        for id in option_ids:
            opt = Optionsymbol.objects.get(pk=id)
            opt.optionscreeners.remove(request.user)
        return redirect(reverse('accounts:dashboard'))

@ login_required
@ csrf_exempt
def RemoveFutureScreenerView(request):
    if request.method == "POST":
        future_ids = request.POST.getlist('id[]')
        for id in future_ids:
            fut = Futuresymbol.objects.get(pk=id)
            fut.futurescreeners.remove(request.user)
        return redirect(reverse('accounts:dashboard'))

@ login_required
@ csrf_exempt
def RemoveIVScreenerView(request):
    if request.method == "POST":
        iv_ids = request.POST.getlist('id[]')
        for id in iv_ids:
            iv = Optionseries.objects.get(pk=id)
            iv.seriesscreeners.remove(request.user)
        return redirect(reverse('accounts:dashboard'))

@ login_required
@ csrf_exempt
def RemoveATMIVScreenerView(request):
    if request.method == "POST":
        atm_iv_ids = request.POST.getlist('id[]')
        for id in atm_iv_ids:
            iv = Optionseries.objects.get(pk=id)
            iv.seriesatmscreeners.remove(request.user)
        return redirect(reverse('accounts:myimpliedatmlist'))

@ login_required
def DashBoardView(request):
    myoptionlist = Optionsymbol.objects.filter(optionscreeners=request.user).order_by('asset', '-expmonthdate', 'optiontype', 'strike')
    myfuturelist = Futuresymbol.objects.filter(futurescreeners=request.user).order_by('asset', '-expmonthdate')
    myimpliedlist = Optionseries.objects.filter(seriesscreeners=request.user)
    myimpliedATMlist = Optionseries.objects.filter(seriesatmscreeners=request.user)
    myoptionlist_count = myoptionlist.count()
    myfuturelist_count = myfuturelist.count()
    myimpliedlist_count = myimpliedlist.count()
    myimpliedATMlist_count = myimpliedATMlist.count()

    context = {
        'myoptionlist_count': myoptionlist_count,
        'myfuturelist_count': myfuturelist_count,
        'myimpliedlist_count': myimpliedlist_count,
        'myimpliedATMlist_count': myimpliedATMlist_count,
    }

    return render(request, 'accounts/mydashboard2.html', context)
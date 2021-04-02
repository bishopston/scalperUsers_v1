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

from accounts.forms import UserAdminCreationForm, CreatePortfolioForm, PortfolioOptionForm, PortfolioFutureForm, PortfolioStockForm, PortfolioOptionUpdateForm, PortfolioOptionUpdateModelForm, PortfolioFutureUpdateModelForm, PortfolioStockUpdateModelForm
from accounts.models import CustomUser, Portfolio, PortfolioOption, PortfolioFuture, PortfolioStock
from option_pricing.models import Option, Future, Stock, Optionsymbol, Futuresymbol, Stocksymbol, Optionseries
from accounts.validators import NumberValidator, UppercaseValidator, LowercaseValidator, SymbolValidator

from datetime import date
from decimal import Decimal

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
    myoptionlist = Optionsymbol.objects.filter(optionscreeners=request.user)
    return render(request,
                  'accounts/myoptionlist.html',
                  {'myoptionlist': myoptionlist})

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
    myfuturelist = Futuresymbol.objects.filter(futurescreeners=request.user)
    return render(request,
                  'accounts/myfuturelist.html',
                  {'myfuturelist': myfuturelist})

@ login_required
def myImpliedList(request):
    myimpliedlist = Optionseries.objects.filter(seriesscreeners=request.user)
    return render(request,
                  'accounts/myimplied.html',
                  {'myimpliedlist': myimpliedlist})

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
    myimpliedATMlist = Optionseries.objects.filter(seriesatmscreeners=request.user)
    return render(request,
                  'accounts/myimpliedatm.html',
                  {'myimpliedATMlist': myimpliedATMlist})

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
                'form': form}

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

    max_options_dates, options_clos_prices, stock_prices, profits, option_debit_credit, option_valuation, option_payoff = ([] for i in range(7))

    for i in options:
        qs_options = Option.objects.filter(optionsymbol=PortfolioOption.objects.get(id=i.id).optionsymbol.id)
        max_options_date = qs_options.aggregate(Max('date'))
        option_strike = json.dumps(qs_options[0].optionsymbol.strike, cls=DecimalEncoder)
        option_type = qs_options[0].optionsymbol.optiontype

        max_options_dates.append(max_options_date['date__max'].strftime("%#d/%#m/%Y"))

        latest_clos = qs_options.filter(date=max_options_date['date__max']).values('closing_price')[0]['closing_price']
        options_clos_prices.append(json.dumps(latest_clos, cls=DecimalEncoder))

        latest_stock = qs_options.filter(date=max_options_date['date__max']).values('stock')[0]['stock']
        stock_prices.append(json.dumps(latest_stock, cls=DecimalEncoder))

        if option_type == 'c':
            if i.position == 'Long':
                profits.append(float(latest_stock) - float(qs_options[0].optionsymbol.strike) - float(i.buysellprice))
            else:
                profits.append(float(qs_options[0].optionsymbol.strike) + float(i.buysellprice) - float(latest_stock))

        if option_type == 'p':
            if i.position == 'Long':                
                profits.append(float(qs_options[0].optionsymbol.strike) - float(latest_stock) - float(i.buysellprice))
            else:
                profits.append(float(latest_stock) + float(i.buysellprice) - float(qs_options[0].optionsymbol.strike))

        option_debit_credit.append(float(100*i.contracts*i.buysellprice))
        option_valuation.append(float(100*i.contracts*latest_clos))
        #option_payoff.append(100*i.contracts*profits[i])

    max_futures_dates, futures_clos_prices, futures_stock_prices, fixing_prices, futures_profits = ([] for i in range(5))

    for i in futures:
        qs_futures = Future.objects.filter(futuresymbol=PortfolioFuture.objects.get(id=i.id).futuresymbol.id)
        max_futures_date = qs_futures.aggregate(Max('date'))

        max_futures_dates.append(max_futures_date['date__max'].strftime("%#d/%#m/%Y"))

        latest_clos = qs_futures.filter(date=max_futures_date['date__max']).values('closing_price')[0]['closing_price']
        futures_clos_prices.append(json.dumps(latest_clos, cls=DecimalEncoder))

        latest_stock = qs_futures.filter(date=max_futures_date['date__max']).values('stock')[0]['stock']
        futures_stock_prices.append(json.dumps(latest_stock, cls=DecimalEncoder))

        latest_fixing_price = qs_futures.filter(date=max_futures_date['date__max']).values('fixing_price')[0]['fixing_price']
        fixing_prices.append(json.dumps(latest_fixing_price, cls=DecimalEncoder))

        if i.position == 'Long':
            if latest_fixing_price > 0:
                futures_profits.append(float(latest_fixing_price) - float(i.buysellprice))
            else:
                futures_profits.append(float(latest_clos) - float(i.buysellprice))
                
        if i.position == 'Short':
            if latest_fixing_price > 0:
                futures_profits.append(float(i.buysellprice) - float(latest_fixing_price))
            else:
                futures_profits.append(float(i.buysellprice) - float(latest_clos))

    max_stocks_dates, stock_stock_prices, stocks_profits = ([] for i in range(3))

    for i in stocks:
        qs_stocks = Stock.objects.filter(stocksymbol=PortfolioStock.objects.get(id=i.id).stocksymbol.id)
        max_stocks_date = qs_stocks.aggregate(Max('date'))
        
        max_stocks_dates.append(max_stocks_date['date__max'].strftime("%#d/%#m/%Y"))
        
        latest_stock = qs_stocks.filter(date=max_stocks_date['date__max']).values('close')[0]['close']
        stock_stock_prices.append(json.dumps(latest_stock, cls=DecimalEncoder))
        
        stocks_profits.append(float(latest_stock)-float(i.buyprice))

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
                    'portfolioOptionForm': portfolioOptionForm,
                    'portfolioFutureForm': portfolioFutureForm,
                    'portfolioStockForm': portfolioStockForm,
                    'max_options_dates': max_options_dates,   
                    'options_clos_prices': options_clos_prices,     
                    'stock_prices': stock_prices,       
                    'profits': profits,    
                    'max_futures_dates': max_futures_dates, 
                    'futures_clos_prices': futures_clos_prices,
                    'futures_stock_prices': futures_stock_prices,
                    'max_stocks_dates': max_stocks_dates,
                    'fixing_prices': fixing_prices,
                    'futures_profits': futures_profits,
                    'max_stocks_dates': max_stocks_dates,
                    'stock_stock_prices': stock_stock_prices,
                    'stocks_profits': stocks_profits,
                    'error_message': 'Please select a valid active option',
                    })


    context = {'portfolio': portfolio,
                'options': options,
                'futures': futures,
                'stocks': stocks,
                'portfolioOptionForm': portfolioOptionForm,
                'portfolioFutureForm': portfolioFutureForm,
                'portfolioStockForm': portfolioStockForm,
                'max_options_dates': max_options_dates,
                'options_clos_prices': options_clos_prices,
                'stock_prices': stock_prices,
                'profits': profits,
                'max_futures_dates': max_futures_dates, 
                'futures_clos_prices': futures_clos_prices,
                'futures_stock_prices': futures_stock_prices,
                'fixing_prices': fixing_prices,
                'futures_profits': futures_profits,
                'max_stocks_dates': max_stocks_dates,
                'stock_stock_prices': stock_stock_prices,
                'stocks_profits': stocks_profits,
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
    return redirect('accounts:portfolio')
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
    return redirect('accounts:portfolio')
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

    max_options_dates, options_clos_prices, stock_prices, profits = ([] for i in range(4))

    for i in options:
        qs_options = Option.objects.filter(optionsymbol=PortfolioOption.objects.get(id=i.id).optionsymbol.id)
        max_options_date = qs_options.aggregate(Max('date'))
        option_strike = json.dumps(qs_options[0].optionsymbol.strike, cls=DecimalEncoder)
        option_type = qs_options[0].optionsymbol.optiontype

        max_options_dates.append(max_options_date['date__max'].strftime("%#d/%#m/%Y"))

        latest_clos = qs_options.filter(date=max_options_date['date__max']).values('closing_price')[0]['closing_price']
        options_clos_prices.append(json.dumps(latest_clos, cls=DecimalEncoder))

        latest_stock = qs_options.filter(date=max_options_date['date__max']).values('stock')[0]['stock']
        stock_prices.append(json.dumps(latest_stock, cls=DecimalEncoder))

        if option_type == 'c':
            if i.position == 'Long':
                profits.append(float(latest_stock) - float(qs_options[0].optionsymbol.strike) - float(i.buysellprice))
            else:
                profits.append(float(qs_options[0].optionsymbol.strike) + float(i.buysellprice) - float(latest_stock))

        if option_type == 'p':
            if i.position == 'Long':                
                profits.append(float(qs_options[0].optionsymbol.strike) - float(latest_stock) - float(i.buysellprice))
            else:
                profits.append(float(latest_stock) + float(i.buysellprice) - float(qs_options[0].optionsymbol.strike))


    max_futures_dates, futures_clos_prices, futures_stock_prices, fixing_prices, futures_profits = ([] for i in range(5))

    for i in futures:
        qs_futures = Future.objects.filter(futuresymbol=PortfolioFuture.objects.get(id=i.id).futuresymbol.id)
        max_futures_date = qs_futures.aggregate(Max('date'))

        max_futures_dates.append(max_futures_date['date__max'].strftime("%#d/%#m/%Y"))

        latest_clos = qs_futures.filter(date=max_futures_date['date__max']).values('closing_price')[0]['closing_price']
        futures_clos_prices.append(json.dumps(latest_clos, cls=DecimalEncoder))

        latest_stock = qs_futures.filter(date=max_futures_date['date__max']).values('stock')[0]['stock']
        futures_stock_prices.append(json.dumps(latest_stock, cls=DecimalEncoder))

        latest_fixing_price = qs_futures.filter(date=max_futures_date['date__max']).values('fixing_price')[0]['fixing_price']
        fixing_prices.append(json.dumps(latest_fixing_price, cls=DecimalEncoder))

        if i.position == 'Long':
            if latest_fixing_price > 0:
                futures_profits.append(float(latest_fixing_price) - float(i.buysellprice))
            else:
                futures_profits.append(float(latest_clos) - float(i.buysellprice))
                
        if i.position == 'Short':
            if latest_fixing_price > 0:
                futures_profits.append(float(i.buysellprice) - float(latest_fixing_price))
            else:
                futures_profits.append(float(i.buysellprice) - float(latest_clos))

    max_stocks_dates, stock_stock_prices, stocks_profits = ([] for i in range(3))

    for i in stocks:
        qs_stocks = Stock.objects.filter(stocksymbol=PortfolioStock.objects.get(id=i.id).stocksymbol.id)
        max_stocks_date = qs_stocks.aggregate(Max('date'))
        
        max_stocks_dates.append(max_stocks_date['date__max'].strftime("%#d/%#m/%Y"))
        
        latest_stock = qs_stocks.filter(date=max_stocks_date['date__max']).values('close')[0]['close']
        stock_stock_prices.append(json.dumps(latest_stock, cls=DecimalEncoder))
        
        stocks_profits.append(float(latest_stock)-float(i.buyprice))

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
                    'portfolioFutureForm': portfolioFutureForm,
                    'max_options_dates': max_options_dates,   
                    'options_clos_prices': options_clos_prices,     
                    'stock_prices': stock_prices,       
                    'profits': profits,    
                    'max_futures_dates': max_futures_dates, 
                    'futures_clos_prices': futures_clos_prices,
                    'futures_stock_prices': futures_stock_prices,
                    'fixing_prices': fixing_prices,
                    'futures_profits': futures_profits,
                    'max_stocks_dates': max_stocks_dates,
                    'stock_stock_prices': stock_stock_prices,
                    'stocks_profits': stocks_profits,
                    'error_future_message': 'Please select a valid active future',
                    })

            else:
                return HttpResponseRedirect(request.path_info)

    context = {'portfolio': portfolio,
                'options': options,
                'futures': futures,
                'stocks': stocks,
                'portfolioOptionForm': portfolioOptionForm,
                'portfolioFutureForm': portfolioFutureForm,
                'portfolioStockForm': portfolioStockForm,
                'max_options_dates': max_options_dates,
                'options_clos_prices': options_clos_prices,
                'stock_prices': stock_prices,
                'profits': profits,
                'max_futures_dates': max_futures_dates, 
                'futures_clos_prices': futures_clos_prices,
                'futures_stock_prices': futures_stock_prices,
                'fixing_prices': fixing_prices,
                'futures_profits': futures_profits,
                'max_stocks_dates': max_stocks_dates,
                'stock_stock_prices': stock_stock_prices,
                'stocks_profits': stocks_profits,
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

    max_options_dates, options_clos_prices, stock_prices, profits = ([] for i in range(4))

    for i in options:
        qs_options = Option.objects.filter(optionsymbol=PortfolioOption.objects.get(id=i.id).optionsymbol.id)
        max_options_date = qs_options.aggregate(Max('date'))
        option_strike = json.dumps(qs_options[0].optionsymbol.strike, cls=DecimalEncoder)
        option_type = qs_options[0].optionsymbol.optiontype

        max_options_dates.append(max_options_date['date__max'].strftime("%#d/%#m/%Y"))

        latest_clos = qs_options.filter(date=max_options_date['date__max']).values('closing_price')[0]['closing_price']
        options_clos_prices.append(json.dumps(latest_clos, cls=DecimalEncoder))

        latest_stock = qs_options.filter(date=max_options_date['date__max']).values('stock')[0]['stock']
        stock_prices.append(json.dumps(latest_stock, cls=DecimalEncoder))

        if option_type == 'c':
            if i.position == 'Long':
                profits.append(float(latest_stock) - float(qs_options[0].optionsymbol.strike) - float(i.buysellprice))
            else:
                profits.append(float(qs_options[0].optionsymbol.strike) + float(i.buysellprice) - float(latest_stock))

        if option_type == 'p':
            if i.position == 'Long':                
                profits.append(float(qs_options[0].optionsymbol.strike) - float(latest_stock) - float(i.buysellprice))
            else:
                profits.append(float(latest_stock) + float(i.buysellprice) - float(qs_options[0].optionsymbol.strike))


    max_futures_dates, futures_clos_prices, futures_stock_prices, fixing_prices, futures_profits = ([] for i in range(5))

    for i in futures:
        qs_futures = Future.objects.filter(futuresymbol=PortfolioFuture.objects.get(id=i.id).futuresymbol.id)
        max_futures_date = qs_futures.aggregate(Max('date'))

        max_futures_dates.append(max_futures_date['date__max'].strftime("%#d/%#m/%Y"))

        latest_clos = qs_futures.filter(date=max_futures_date['date__max']).values('closing_price')[0]['closing_price']
        futures_clos_prices.append(json.dumps(latest_clos, cls=DecimalEncoder))

        latest_stock = qs_futures.filter(date=max_futures_date['date__max']).values('stock')[0]['stock']
        futures_stock_prices.append(json.dumps(latest_stock, cls=DecimalEncoder))

        latest_fixing_price = qs_futures.filter(date=max_futures_date['date__max']).values('fixing_price')[0]['fixing_price']
        fixing_prices.append(json.dumps(latest_fixing_price, cls=DecimalEncoder))

        if i.position == 'Long':
            if latest_fixing_price > 0:
                futures_profits.append(float(latest_fixing_price) - float(i.buysellprice))
            else:
                futures_profits.append(float(latest_clos) - float(i.buysellprice))
                
        if i.position == 'Short':
            if latest_fixing_price > 0:
                futures_profits.append(float(i.buysellprice) - float(latest_fixing_price))
            else:
                futures_profits.append(float(i.buysellprice) - float(latest_clos))

    max_stocks_dates, stock_stock_prices, stocks_profits = ([] for i in range(3))

    for i in stocks:
        qs_stocks = Stock.objects.filter(stocksymbol=PortfolioStock.objects.get(id=i.id).stocksymbol.id)
        max_stocks_date = qs_stocks.aggregate(Max('date'))
        
        max_stocks_dates.append(max_stocks_date['date__max'].strftime("%#d/%#m/%Y"))
        
        latest_stock = qs_stocks.filter(date=max_stocks_date['date__max']).values('close')[0]['close']
        stock_stock_prices.append(json.dumps(latest_stock, cls=DecimalEncoder))
        
        stocks_profits.append(float(latest_stock)-float(i.buyprice))

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
                    'portfolioOptionForm': portfolioOptionForm,
                    'portfolioFutureForm': portfolioFutureForm,
                    'portfolioStockForm': portfolioStockForm,
                    'max_options_dates': max_options_dates,   
                    'options_clos_prices': options_clos_prices,     
                    'stock_prices': stock_prices,       
                    'profits': profits,    
                    'max_futures_dates': max_futures_dates, 
                    'futures_clos_prices': futures_clos_prices,
                    'futures_stock_prices': futures_stock_prices,
                    'fixing_prices': fixing_prices,
                    'futures_profits': futures_profits,
                    'max_stocks_dates': max_stocks_dates,
                    'stock_stock_prices': stock_stock_prices,
                    'stocks_profits': stocks_profits,
                    'error_stock_message': 'Please select a valid stock',
                    })

            else:
                return HttpResponseRedirect(request.path_info)

    context = {'portfolio': portfolio,
                'options': options,
                'futures': futures,
                'stocks': stocks,
                'portfolioOptionForm': portfolioOptionForm,
                'portfolioFutureForm': portfolioFutureForm,
                'portfolioStockForm': portfolioStockForm,
                'max_options_dates': max_options_dates,
                'options_clos_prices': options_clos_prices,
                'stock_prices': stock_prices,
                'profits': profits,
                'max_futures_dates': max_futures_dates, 
                'futures_clos_prices': futures_clos_prices,
                'futures_stock_prices': futures_stock_prices,
                'fixing_prices': fixing_prices,
                'futures_profits': futures_profits,
                'max_stocks_dates': max_stocks_dates,
                'stock_stock_prices': stock_stock_prices,
                'stocks_profits': stocks_profits,
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
    return redirect('accounts:portfolio')

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

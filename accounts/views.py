from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from django.http import HttpResponse, JsonResponse
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

from accounts.forms import UserAdminCreationForm, CreatePortfolioForm
from accounts.models import CustomUser, Portfolio
from option_pricing.models import Optionsymbol, Futuresymbol, Optionseries
from accounts.validators import NumberValidator, UppercaseValidator, LowercaseValidator, SymbolValidator


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
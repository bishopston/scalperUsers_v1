from django.shortcuts import render


def home(request):
    return render(request, 'option_pricing/home.html')
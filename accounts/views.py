from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from accounts.forms import UserAdminCreationForm

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

def profile(request):
    return render(request,
                  'registration/profile.html',
                  {'section': 'profile'})
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import UserLoginForm


app_name = 'accounts'


urlpatterns = [
    path('register/', views.register, name='register'),
    #path('profile/', views.profile, name='profile'),
    path('login/', auth_views.LoginView.as_view(template_name="registration/login.html"), name='login'),
]
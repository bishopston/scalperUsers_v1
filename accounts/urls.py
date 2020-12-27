from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import EmailValidationView, PasswordValidationView
from .forms import UserLoginForm
from django.views.decorators.csrf import csrf_exempt


app_name = 'accounts'


urlpatterns = [
    path('register/', views.register, name='register'),
    #path('profile/', views.profile, name='profile'),
    path('login/', auth_views.LoginView.as_view(template_name="registration/login.html"), name='login'),
    path('activate/<uidb64>/<token>/',views.activate, name='activate'),
    path('validate-email/', csrf_exempt(EmailValidationView.as_view()),
         name='validate_email'),    
    path('validate-password/', csrf_exempt(PasswordValidationView.as_view()),
         name='validate_password'),  
]
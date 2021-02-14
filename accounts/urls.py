from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import EmailValidationView, PasswordValidationView
from .forms import UserLoginForm
from django.views.decorators.csrf import csrf_exempt


app_name = 'accounts'


urlpatterns = [
     path('register/', views.register, name='register'),
     path('login/', auth_views.LoginView.as_view(template_name="registration/login.html"), name='login'),
     path('activate/<uidb64>/<token>/',views.activate, name='activate'),
     path('myoptionscreeners/', views.myOptionScreeners, name='myoptionscreeners'),
     path('myfuturescreeners/', views.myFutureScreeners, name='myfuturescreeners'),
     path('myimpliedscreeners/', views.myImpliedScreeners, name='myimpliedscreeners'),
     path('myoptionlist/', views.myOptionList, name='myoptionlist'),
     path('myfuturelist/', views.myFutureList, name='myfuturelist'),
     path('myimpliedlist/', views.myImpliedList, name='myimpliedlist'),
     path('myimpliedatmlist/', views.myImpliedATMList, name='myimpliedatmlist'),
     path('fav/<int:id>/', views.favourite_add, name='favourite_add'),
     path('like/', views.like_option, name='like_option'),
     path('user/favourites/', views.favourite_list, name='favourite_list'),
     path('user/likes/', views.like_list, name='like_list'),
     path('validate-email/', csrf_exempt(EmailValidationView.as_view()),
          name='validate_email'),    
     path('validate-password/', csrf_exempt(PasswordValidationView.as_view()),
          name='validate_password'),  
]
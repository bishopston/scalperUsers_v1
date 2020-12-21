from django.urls import path
from . import views

app_name = 'option_pricing'

urlpatterns = [
    path('', views.home, name="home"),
]
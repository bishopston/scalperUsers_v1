from django.urls import path
from . import views
from option_pricing.views import OptionScreenersListCBV
app_name = 'option_pricing'

urlpatterns = [
    path('', views.home, name="home"),
    #path('options/', views.OptionView, name='option'),
    #path('optionsajax/', views.OptionAjaxView, name='option_ajax'),
    path('options/<str:optionsymbol>/', views.OptionScreenerDetail, name='option_screener_detail'),
    #path('options/greatestOI/', views.OptionGreatestOI, name='option_greatestOI'),
    path('options/chart/<str:tradesymbol>/', views.OptionJSChartView, name="option_jschart"),
    path('options/chart_vol/<str:tradesymbol>/', views.OptionJSChartVolView, name="option_vol_jschart"),
    path('options/deltachart/<str:tradesymbol>/', views.OptionJSDeltaChartView, name="option_delta_jschart"),
    path('options/gammachart/<str:tradesymbol>/', views.OptionJSGammaChartView, name="option_gamma_jschart"),
    path('options/thetachart/<str:tradesymbol>/', views.OptionJSThetaChartView, name="option_theta_jschart"),
    path('options/vegachart/<str:tradesymbol>/', views.OptionJSVegaChartView, name="option_vega_jschart"),
    path('options/impliedchart/<str:tradesymbol>/', views.OptionJSImpliedChartView, name="option_implied_jschart"),
    path('options/', OptionScreenersListCBV.as_view(), name='myoptionscreenerlistcbv'),
    path('futures/', views.FutureView, name='future'),
    path('futures/<str:futuresymbol>/', views.FutureScreenerDetail, name='future_screener_detail'),
    path('futures/chart/<str:tradesymbol>/', views.FutureJSChartView, name="future_jschart"),
    path('futures/chart_vol/<str:tradesymbol>/', views.FutureJSChartVolView, name="future_vol_jschart"),
    path('futures/spotchart/<str:tradesymbol>/', views.FutureJSSportChartView, name="future_spot_jschart"),
]
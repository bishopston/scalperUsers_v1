from django.urls import path
from . import views
from option_pricing.views import OptionScreenersListCBV, FutureScreenersListCBV, ImpliedScreenerListCBV, ImpliedScreenerATMListCBV, OptionDescendingOI, FutureDescendingOI, OptionDailyStatsView
app_name = 'option_pricing'

urlpatterns = [
    path('', views.home, name="home"),
    #path('options/', views.OptionView, name='option'),
    #path('optionsajax/', views.OptionAjaxView, name='option_ajax'),
    #test urls for greatest OI templates based on infinite scroll
    path('options/greatestOI/', views.OptionGreatestOI, name='option_greatestOI'),
    path('options/greatestOIfetch/', views.OptionGreatestOIFetch, name='option_greatestOI_fetch'),
    #urls for option daily stats
    path('options/dailystats/', views.OptionDailyStatsView, name='optiondailystats'),
    path('options/dailyvolumecallgraph/', views.OptionDailyGraphCallView, name='dailyvolumecall'),
    path('options/dailyvolumeputgraph/', views.OptionDailyGraphPutView, name='dailyvolumeput'),
    path('options/dailyvolumeallgraph/', views.OptionDailyVolumeGraphAllView, name='dailyvolumeall'),
    path('options/dailyvolumecallputgraph/', views.OptionDailyVolumeGraphCallPutView, name='dailyvolumecallput'),
    path('options/dailyvolumeexpcallgraph/', views.OptionDailyVolumeGraphExpCallView, name='dailyvolumeexpcall'),
    path('options/dailyvolumeexpputgraph/', views.OptionDailyVolumeGraphExpPutView, name='dailyvolumeexpput'),
    #path('options/descendingOI/', views.OptionDescendingOI, name='option_descendingOI'),
    #urls for option historical stats
    path('options/historicalstats/', views.OptionHistoricalStatsView, name='optionhiststats'),
    #urls for greatest OI templates
    path('options/descendingOI/', OptionDescendingOI.as_view(), name='option_descendingOI'),
    path('futures/descendingOI/', FutureDescendingOI.as_view(), name='future_descendingOI'),
    #options screeners urls
    path('options/<str:optionsymbol>/', views.OptionScreenerDetail, name='option_screener_detail'),
    path('options/chart/<str:tradesymbol>/', views.OptionJSChartView, name="option_jschart"),
    path('options/chart_vol/<str:tradesymbol>/', views.OptionJSChartVolView, name="option_vol_jschart"),
    path('options/deltachart/<str:tradesymbol>/', views.OptionJSDeltaChartView, name="option_delta_jschart"),
    path('options/gammachart/<str:tradesymbol>/', views.OptionJSGammaChartView, name="option_gamma_jschart"),
    path('options/thetachart/<str:tradesymbol>/', views.OptionJSThetaChartView, name="option_theta_jschart"),
    path('options/vegachart/<str:tradesymbol>/', views.OptionJSVegaChartView, name="option_vega_jschart"),
    path('options/impliedchart/<str:tradesymbol>/', views.OptionJSImpliedChartView, name="option_implied_jschart"),
    path('options/', OptionScreenersListCBV.as_view(), name='myoptionscreenerlistcbv'),   
    #iv screeners urls
    #path('impliedvolscreeners_a/', views.ImpliedperStrikeScreenerView, name="impliedvolscreeners_a"),
    #path('impliedvolscreeners/', views.ImpliedScreenerView, name="impliedvolscreeners"),
    path('impliedvolatilitysmile/<str:asset>/<str:optiontype>/<int:expmonth>/<int:expyear>/', views.ImpliedSmileView, name="impliedvolsmile"),
    path('ivscreeners/<str:asset>/<str:optiontype>/<int:expmonth>/<int:expyear>/', views.IVscreenerChartView, name="ivscreenerchartview"),
    path('impliedvolscreeners/', ImpliedScreenerListCBV.as_view(), name='myseriesscreenerlistcbv'),
    path('impliedvolatmscreeners/', ImpliedScreenerATMListCBV.as_view(), name='myseriesatmscreenerlistcbv'),
    path('impliedvolatilityatm/<str:asset>/<str:optiontype>/<int:expmonth>/<int:expyear>/', views.ImpliedATMView, name="impliedvolatm"),
    path('ivatm/<str:asset>/<str:optiontype>/<int:expmonth>/<int:expyear>/', views.IVATMChartView, name="ivatmchartview"),
    #futures screeners urls
    path('futures/', FutureScreenersListCBV.as_view(), name='myfuturescreenerlistcbv'),
    path('futures/<str:futuresymbol>/', views.FutureScreenerDetail, name='future_screener_detail'),
    path('futures/chart/<str:tradesymbol>/', views.FutureJSChartView, name="future_jschart"),
    path('futures/chart_vol/<str:tradesymbol>/', views.FutureJSChartVolView, name="future_vol_jschart"),
    path('futures/spotchart/<str:tradesymbol>/', views.FutureJSSportChartView, name="future_spot_jschart"),
]
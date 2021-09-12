from django.urls import path
from django.views.generic import TemplateView
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
    #urls for options daily stats
    path('options/dailystats/', views.OptionDailyStatsView, name='optiondailystats'),
    path('options/dailyvolumecallgraph/', views.OptionDailyGraphCallView, name='dailyvolumecall'),
    path('options/dailyvolumeputgraph/', views.OptionDailyGraphPutView, name='dailyvolumeput'),
    path('options/dailyvolumeallgraph/', views.OptionDailyVolumeGraphAllView, name='dailyvolumeall'),
    path('options/dailyvolumecallputgraph/', views.OptionDailyVolumeGraphCallPutView, name='dailyvolumecallput'),
    path('options/dailyvolumeexpcallgraph/', views.OptionDailyVolumeGraphExpCallView, name='dailyvolumeexpcall'),
    path('options/dailyvolumeexpputgraph/', views.OptionDailyVolumeGraphExpPutView, name='dailyvolumeexpput'),
    path('options/dailyopenintcallgraph/', views.OptionDailyOpenIntGraphCallView, name='dailyopenintcall'),
    path('options/dailyopenintputgraph/', views.OptionDailyOpenIntGraphPutView, name='dailyopenintput'),
    #path('options/descendingOI/', views.OptionDescendingOI, name='option_descendingOI'),
    #urls for options historical stats
    path('options/historicalstats/', views.OptionHistoricalStatsView, name='optionhiststats'),
    path('options/histvolallcallstats/', views.OptionHistVolumeGraphCallAllView, name='optionhistvolallcallstats'),
    path('options/histvolallputstats/', views.OptionHistVolumeGraphPutAllView, name='optionhistvolallputstats'),
    path('options/histvolcallstats/<int:assetid>/', views.OptionHistVolumeGraphCallAssetView, name='optionhistvolassetcallstats'),
    path('options/histvolputstats/<int:assetid>/', views.OptionHistVolumeGraphPutAssetView, name='optionhistvolassetputstats'),
    path('options/histopenintallcallstats/', views.OptionHistOpenIntGraphCallAllView, name='optionhistopenintallcallstats'),
    path('options/histopenintallputstats/', views.OptionHistOpenIntGraphPutAllView, name='optionhistopenintallputstats'),
    path('options/histopenintcallstats/<int:assetid>/', views.OptionHistOpenIntGraphCallAssetView, name='optionhistopenintassetcallstats'),
    path('options/histopenintputstats/<int:assetid>/', views.OptionHistOpenIntGraphPutAssetView, name='optionhistopenintassetputstats'),
    path('options/callputmonthlyallratio/', views.OptionCallPutMonthlyRatioAllView, name='callputmonthlyallratio'),
    #urls for futures daily stats
    path('futures/dailystats/', views.FutureDailyStatsView, name='futuredailystats'),
    path('futures/dailyvolumefuturesgraph/', views.FutureDailyGraphVolumeView, name='dailyvolumefutures'),
    path('futures/seriesvolumefuturesgraph/', views.FutureDailyVolumeGraphExpAllView, name='seriesvolumefuturesall'),
    path('futures/seriesvolumefuturesftsegraph/', views.FutureDailyVolumeGraphExpFtseView, name='seriesvolumefuturesftse'),
    path('futures/dailyopenintfuturesgraph/', views.FutureDailyGraphOpenIntView, name='dailyopenintfutures'),
    #urls for futures historical stats
    path('futures/historicalstats/', views.FutureHistoricalStatsView, name='futurehiststats'),
    path('futures/histvolallfuturestats/', views.FutureHistVolumeGraphAllView, name='futurehistvolallstats'),
    path('futures/histopenintallfuturestats/', views.FutureHistOpenIntGraphAllView, name='futurehistopenintallstats'),
    path('futures/historical/<str:asset>/', views.FutureHistAssetView, name='futurehistasset'),
    path('futures/histvolassetstats/<str:asset>/', views.FutureHistVolumeGraphAssetView, name='futurehistvolassetstats'),
    path('futures/histopenintassetstats/<str:asset>/', views.FutureHistOpenIntGraphAssetView, name='futurehistopenintassetstats'),
    #urls for greatest OI templates
    path('options/descendingOI/', OptionDescendingOI.as_view(), name='option_descendingOI'),
    path('futures/descendingOI/', FutureDescendingOI.as_view(), name='future_descendingOI'),
    #options screeners urls
    path('options/searchsymbol/', views.OptionSearchSymbolView, name='option_search_symbol'),
    #path('options/searchsymbol2/', views.OptionSearchSymbolView2, name='option_search_symbol2'),
    path('options/searchsymbolautocomplete/', views.OptionSearchSymbolAutoCompleteView, name='option_search_symbol_autocomplete'),
    path('options/<str:optionsymbol>/', views.OptionScreenerDetail, name='option_screener_detail'),
    path('options/chart/<str:tradesymbol>/', views.OptionJSChartView, name="option_jschart"),
    path('options/chart_vol/<str:tradesymbol>/', views.OptionJSChartVolView, name="option_vol_jschart"),
    path('options/deltachart/<str:tradesymbol>/', views.OptionJSDeltaChartView, name="option_delta_jschart"),
    path('options/gammachart/<str:tradesymbol>/', views.OptionJSGammaChartView, name="option_gamma_jschart"),
    path('options/thetachart/<str:tradesymbol>/', views.OptionJSThetaChartView, name="option_theta_jschart"),
    path('options/vegachart/<str:tradesymbol>/', views.OptionJSVegaChartView, name="option_vega_jschart"),
    path('options/impliedchart/<str:tradesymbol>/', views.OptionJSImpliedChartView, name="option_implied_jschart"),
    path('options/', OptionScreenersListCBV.as_view(), name='myoptionscreenerlistcbv'),
    path('options/screenerdata/', views.OptionScreenersDataView, name='optionscreenerdata'),   
    path('optionsymbol-export-csv/<str:optionsymbol>/', views.OptionSymbolExportCSV, name='optionsymbol-export-csv'),
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
    path('futuresymbol-export-csv/<str:futuresymbol>/', views.FutureSymbolExportCSV, name='futuresymbol-export-csv'),
    #spot markets urls
    path('spotmarkets/', views.StockHistoricalView, name='stock_historical'),
    path('stocks/chart/<str:tradesymbol>/', views.StockJSChartView, name="stock_jschart"),
    path('stocks/chart_vol/<str:tradesymbol>/', views.StockJSChartVolView, name="stock_vol_jschart"),
    path('spotmarkets/<str:asset>/', views.StockHistoricalAssetView, name='stock_historical_asset'),
    #footer urls
    path('privacy-policy/', TemplateView.as_view(template_name="option_pricing/privacy_policy.html"), name='privacy-policy'),
    path('terms-of-use/', TemplateView.as_view(template_name="option_pricing/terms_of_use.html"), name='terms-of-use'),
    path('cookie-policy/', TemplateView.as_view(template_name="option_pricing/cookie_policy.html"), name='cookie-policy'),
]
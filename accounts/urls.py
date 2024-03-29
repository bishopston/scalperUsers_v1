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
     path('myimpliedatmscreeners/', views.myImpliedATMScreeners, name='myimpliedatmscreeners'),
     path('myoptionlist/', views.myOptionList, name='myoptionlist'),
     path('myfuturelist/', views.myFutureList, name='myfuturelist'),
     path('myimpliedlist/', views.myImpliedList, name='myimpliedlist'),
     path('myimpliedatmlist/', views.myImpliedATMList, name='myimpliedatmlist'),
     #path('mydashboard/', views.myDashboard, name='mydashboard'),
     path('fav/<int:id>/', views.favourite_add, name='favourite_add'),
     path('like/', views.like_option, name='like_option'),
     path('user/favourites/', views.favourite_list, name='favourite_list'),
     path('user/likes/', views.like_list, name='like_list'),
     path('validate-email/', csrf_exempt(EmailValidationView.as_view()),
          name='validate_email'),    
     path('validate-password/', csrf_exempt(PasswordValidationView.as_view()),
          name='validate_password'),  
     #portfolio urls
     path('portfolio/', views.PortfolioView, name='portfolio'),
     path('portfolio-delete/', views.DeletePortfolioView, name='portfolio-delete'),
     path('portfolio/<int:portfolio_id>', views.PortfolioDetailView, name='portfolio-detail'),
     path('portfoliooption-delete/', views.DeletePortfolioOptionView, name='portfolio-option-delete'),
     path('portfoliooption-update/<int:portfolio_id>/<int:portfoliooption_id>/', views.UpdatePortfolioOptionView, name='portfolio-option-update'),
     path('portfoliofuture/<int:portfolio_id>/', views.PortfolioFutureDetailView, name='portfolio-future-detail'),
     path('portfoliofuture-delete/', views.DeletePortfolioFutureView, name='portfolio-future-delete'),
     path('portfoliofuture-update/<int:portfolio_id>/<int:portfoliofuture_id>/', views.UpdatePortfolioFutureView, name='portfolio-future-update'),
     path('portfoliostock/<int:portfolio_id>/', views.PortfolioStockDetailView, name='portfolio-stock-detail'),
     path('portfoliostock-delete/', views.DeletePortfolioStockView, name='portfolio-stock-delete'),
     path('portfoliostock-update/<int:portfolio_id>/<int:portfoliostock_id>/', views.UpdatePortfolioStockView, name='portfolio-stock-update'),
     path('portfolio-valuation/<int:portfolio_id>/', views.PortfolioValuationView, name='portfolio-valuation'),
     path('portfolio-valuation-pdf/<int:portfolio_id>/', views.PortfolioValuationPDFView, name='portfolio-valuation-pdf'),
     # path('myportfolio-pdf/', views.MyPortfolioPDFView, name='myportfolio-pdf'),
     path('test-pdf/', views.render_pdf_view, name='test-pdf'),
     path('dashboard/', views.DashBoardView, name='dashboard'),
     path('optscreener-remove/', views.RemoveOptionScreenerView, name='option-screener-remove'),
     path('futscreener-remove/', views.RemoveFutureScreenerView, name='future-screener-remove'),
     path('ivscreener-remove/', views.RemoveIVScreenerView, name='iv-screener-remove'),
     path('atmivscreener-remove/', views.RemoveATMIVScreenerView, name='atmiv-screener-remove'),
]
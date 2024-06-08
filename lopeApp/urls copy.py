from django.urls import path
from lopeApp import views
from .background_tasks import start_background_tasks 
start_background_tasks()

urlpatterns = [
    path('', views.home, name="home"),
   
    path('about/', views.about, name='about'),
    path('plans/', views.plans, name='plans'),
    path('membership/', views.auth_plans, name='auth_plans'),
    
    
    path('contact/', views.contact_form, name='contact_form'),
    
    path('register/', views.register_view, name='register'),
    path('accounts/login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    path('deposit/', views.deposit_view, name='deposit'),
    path('deposit-history/', views.deposit_history, name='deposit_history'),
    path('deposit_confirmation/success', views.deposit_confirmation_success, name='deposit_confirmation_success'),
    path('deposit/success/', views.deposit_success_view, name='deposit_success'),
    path('manage_deposits/', views.manage_deposits, name='manage_deposits'),
    path('confirm_deposit', views.confirm_deposit, name='confirm_deposit'),  
    
    
    path('manage_withdrawals/', views.manage_withdrawals, name='manage_withdrawals'),
    path('withdrawal/success/', views.withdrawal_success, name='withdrawal_success'),
    path('withdrawal/', views.withdrawal_view, name='withdrawal'),
    path('withdrawal-history/', views.withdrawal_history, name='withdrawal_history'),
    

    path('earnings/', views.earning_history, name='earnings'),
    
    path('referal/<str:username>/', views.referal, name='referal'),
    
    # success urls
    path('login/success/', views.login_success_view, name='login_success'),
    path('registration/success/', views.registration_success_view, name='registration_success'),
    
    
    path('dashboard/', views.dashboard, name='dashboard'),
    
    
    path('send_bonus/', views.send_bonus, name='send_bonus'),
    path('send-monthly-offer/', views.send_monthly_offer, name='send_monthly_offer'),
    path('send_new_month_message/', views.send_new_month_message, name='send_new_month_message'),
    
]

'''from django.urls import path
from . import views'''
'''
urlpatterns = [
    path('main/', views.home_view, name='home'),  # main.html as homepage
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
'''


'''urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('main', views.home_view, name='accounts/main'),
    path('user_dashboard/', views.dashboard_view, name='dashboard'),
    path('buy/<str:plan_name>/', views.select_plan_view, name='buy_plan'),# 👈 Home page (main.html)
]'''
'''
urlpatterns = [
    path('', views.main_page, name='main'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('payments/', views.payments_view, name='payments'),
    path('buy_plan/<int:plan_id>/', views.buy_plan_view, name='buy_plan'),
]'''
'''
urlpatterns = [
    path('', views.custom_login_view, name='home'),
    path('login/', views.custom_login_view, name='login'),
    path('dashboard/', views.user_dashboard_view, name='dashboard'),
    path('payments/', views.payments_view, name='payments'),
    path('buy_plan/<int:plan_id>/', views.buy_plan_view, name='buy_plan'),
    path('commission/', views.commission_view, name='commission'),
    path('courses/', views.courses_view, name='courses'),
]
'''
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import payfast_payment_view

urlpatterns = [
    path('', views.home_view, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login.html/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('courses/', views.courses_view, name='courses'),
    path('buy_plan/<int:plan_id>/', views.buy_plan_view, name='buy_plan'),
    path('commission/', views.commission_view, name='commission'),
    path('team-reward/', views.team_reward_view, name='rewards'),
    path('payments/', views.payments_view, name='payments'),
    path('privacy-policy/', views.privacy_policy_view, name='privacy_policy'),
    path('terms-conditions/', views.terms_conditions_view, name='terms_conditions'),
    # path('pay/', views.pay_with_payfast, name='pay'),
    # path('payfast/return/', views.payment_return, name='payment_return'),
    # path('payfast/cancel/', views.payment_cancel, name='payment_cancel'),
]
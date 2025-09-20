from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path("dashboard/", views.user_dashboard, name="dashboard"),
    path('courses/', views.courses_view, name='courses'),
    path('buy_plan/<int:plan_id>/', views.buy_plan_view, name='buy_plan'),
    path('commission/', views.commission_view, name='commission'),
    path('team-reward/', views.team_reward_view, name='rewards'),
    path('payments/', views.payments_view, name='payments'),
    path('privacy-policy/', views.privacy_policy_view, name='privacy_policy'),
    path('terms-conditions/', views.terms_conditions_view, name='terms_conditions'),
    path('manual-payment/', views.manual_payment_view, name='manual_payment'),
    path('manual-payment/<int:plan_id>/', views.manual_payment_view, name='manual_payment'),
    path('password_reset/', 
         views.CustomPasswordResetView.as_view(
            template_name='password_reset.html',
            subject_template_name='registration/password_reset_subject.txt'
         ), 
         name='password_reset'),
    path('password_reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), 
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', 
         views.CustomPasswordResetConfirmView.as_view(), 
         name='password_reset_confirm'),
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), 
         name='password_reset_complete'),
    path('csrf-refresh/', views.csrf_refresh, name='csrf_refresh'),

]
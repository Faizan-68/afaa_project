### Directory: accounts/views.py

from django.shortcuts import render, redirect, get_object_or_404
from .models import Commission, Referral, UserProfile, PLAN_PRICES
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import Plan, UserPlan
from django.contrib import messages
from django.conf import settings
from django.contrib import messages
from .models import UserProfile, Referral
from django.contrib.auth.models import User
from .forms import SignUpForm  
from .models import TeamReward
import hashlib


def home_view(request):
    return render(request, 'main.html')

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)

            email = form.cleaned_data.get('email')
            referral_code = form.cleaned_data.get('referral_code')

            user.email = email
            user.save()

            referred_by = None
            if referral_code:
                try:
                    referred_by = User.objects.get(username=referral_code)
                except User.DoesNotExist:
                    referred_by = None

            profile = UserProfile.objects.create(
                user=user,
                plan='BASIC',
                referred_by=referred_by
            )

            level_1 = referred_by
            level_2 = level_3 = None
            if level_1:
                level_2 = level_1.userprofile.referred_by
                if level_2:
                    level_3 = level_2.userprofile.referred_by

            Referral.objects.create(
                referred=user,
                level_1=level_1,
                level_2=level_2,
                level_3=level_3
            )

            login(request, user)
            messages.success(request, "Successfully registered! Welcome to Afaa Elevate.")
            return redirect('dashboard')
    else:
        form = SignUpForm()

    return render(request, 'signup.html', {'form': form})


# @login_required
def dashboard_view(request):
    user_plans = UserPlan.objects.filter(user=request.user)
    return render(request, 'user_dashboard.html', {'user_plans': user_plans})

# @login_required
def courses_view(request):
    plans = Plan.objects.all()
    return render(request, 'courses.html', {'plans': plans})

# @login_required
def buy_plan_view(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id)
    UserPlan.objects.create(user=request.user, plan=plan)

    # Update the user’s plan in profile
    profile = UserProfile.objects.get(user=request.user)
    profile.plan = plan.name.upper()
    profile.save()

    # Trigger commission logic
    calculate_commissions(request.user)

    return redirect('dashboard')

# @login_required
def commission_view(request):
    # commissions = Commission.objects.filter(user=request.user).order_by('-id')
    return render(request, 'commission.html')


# @login_required

def team_reward_view(request):
    # rewards = TeamReward.objects.all().order_by('referrals_required')
    return render(request, 'team_reward.html')


def privacy_policy_view(request):
    return render(request, 'privacy-policy.html')

def terms_conditions_view(request):
    return render(request, 'terms-conditions.html')

# @login_required
def payments_view(request):
    user = request.user

    # Example dummy payment data — replace with actual query from Payment model
    payments = [
        {'id': 1, 'amount': 2500, 'status': 'Success', 'date': '2025-08-01'},
        {'id': 2, 'amount': 1500, 'status': 'Pending', 'date': '2025-07-25'},
    ]

    return render(request, 'payments.html', {'payments': payments})

def payfast_payment_view(request):
    merchant_id = 'YOUR_MERCHANT_ID'
    secure_key = 'YOUR_SECURE_KEY'
    amount = '100'  # PKR
    order_id = '12345'

    post_data = {
        'merchant_id': merchant_id,
        'order_id': order_id,
        'amount': amount,
        'return_url': 'http://127.0.0.1:8000/payment-success/',
        'cancel_url': 'http://127.0.0.1:8000/payment-cancel/',
    }

    # Create a secure hash
    hash_string = f"{merchant_id}&{order_id}&{amount}&{post_data['return_url']}&{secure_key}"
    post_data['secure_hash'] = hashlib.sha256(hash_string.encode()).hexdigest()

    return render(request, 'payment_redirect.html', {'post_data': post_data})

def payment_success(request):
    return render(request, 'success.html')

def payment_cancel(request):
    return render(request, 'cancel.html')

COMMISSION_RATES = {
    'BASIC':   {1: 0.40, 2: 0.08, 3: 0.02},
    'STANDARD': {1: 0.42, 2: 0.08, 3: 0.02},
    'ADVANCE': {1: 0.44, 2: 0.08, 3: 0.02},
    'PRO':     {1: 0.46, 2: 0.08, 3: 0.02},
}

def calculate_commissions(buyer):
    user_profile = UserProfile.objects.get(user=buyer)
    plan_type = user_profile.plan
    plan_price = PLAN_PRICES[plan_type]
    referral = Referral.objects.get(referred=buyer)

    for level, referrer in enumerate([referral.level_1, referral.level_2, referral.level_3], start=1):
        if referrer:
            referrer_plan = UserProfile.objects.get(user=referrer).plan
            commission_percent = get_commission_percentage(referrer_plan, plan_type, level)
            amount = plan_price * commission_percent
            Commission.objects.create(user=referrer, referred_user=buyer, level=level, amount=amount)

def get_commission_percentage(referrer_plan, sold_plan, level):
    RATE_TABLE = {
        'BASIC':   { 'BASIC': {1: 0.40, 2: 0.08, 3: 0.02}, 'STANDARD': {1: 0.42, 2: 0.08, 3: 0.02}, 'ADVANCE': {1: 0.44, 2: 0.08, 3: 0.02}, 'PRO': {1: 0.46, 2: 0.08, 3: 0.02}, },
        'STANDARD': { 'BASIC': {1: 0.40}, 'STANDARD': {1: 0.45}, 'ADVANCE': {1: 0.47}, 'PRO': {1: 0.50, 2: 0.10} },
        'ADVANCE':  { 'BASIC': {1: 0.42}, 'STANDARD': {1: 0.48}, 'ADVANCE': {1: 0.52, 2: 0.10}, 'PRO': {1: 0.55, 2: 0.10} },
        'PRO':      { 'BASIC': {1: 0.45}, 'STANDARD': {1: 0.52}, 'ADVANCE': {1: 0.56, 2: 0.10}, 'PRO': {1: 0.60, 2: 0.10} },
    }
    return RATE_TABLE.get(referrer_plan, {}).get(sold_plan, {}).get(level, 0)

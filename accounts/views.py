# accounts/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import SignUpForm
from .models import Plan, UserPlan, UserProfile, Referral, Commission, TeamReward, Payment, Course, SiteSetting
from .referrals import handle_successful_referral
from django.core.files.storage import FileSystemStorage
from django.db.models import Sum, Count, Q

from django.db import IntegrityError, transaction
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import login as auth_login
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import time

def csrf_failure_view(request, reason=""):
    """Custom CSRF failure handler with user-friendly error message."""
    from django.shortcuts import render, redirect
    from django.contrib import messages
    
    # Add helpful error message
    if reason == "CSRF_COOKIE_NOT_SET":
        messages.error(request, 
            "Security token missing. Please enable cookies and try again.")
    elif reason == "CSRF_TOKEN_MISSING":
        messages.error(request, 
            "Security token missing. Please refresh the page and try again.")
    elif reason == "CSRF_TOKEN_INCORRECT":
        messages.error(request, 
            "Your session has expired. Please refresh the page and try again.")
    else:
        messages.error(request, 
            "Security verification failed. Please refresh the page and try again.")
    
    # Try to redirect back to where they came from, or go to login
    referer = request.META.get('HTTP_REFERER')
    if referer and 'logout' not in referer:
        return redirect(referer)
    else:
        return redirect('login')

from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET"])
def csrf_refresh(request):
    """Endpoint to refresh CSRF token for AJAX requests."""
    token = get_token(request)
    return JsonResponse({
        'csrf_token': token,
        'success': True
    })

class CustomPasswordResetView(PasswordResetView):
    template_name = 'password_reset.html'
    
    def dispatch(self, request, *args, **kwargs):
        """Add rate limiting to prevent abuse."""
        # Simple rate limiting using session
        session_key = 'password_reset_attempts'
        current_time = time.time()
        
        if session_key in request.session:
            attempts = request.session[session_key]
            # Allow max 3 attempts per hour
            recent_attempts = [t for t in attempts if current_time - t < 3600]  # 1 hour
            
            if len(recent_attempts) >= 3:
                messages.error(request, 
                    'Too many password reset attempts. Please wait an hour before trying again.')
                return redirect('login')
            
            request.session[session_key] = recent_attempts
        else:
            request.session[session_key] = []
        
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        """Add success message and handle email sending with error handling."""
        try:
            # Record this attempt
            session_key = 'password_reset_attempts'
            attempts = self.request.session.get(session_key, [])
            attempts.append(time.time())
            self.request.session[session_key] = attempts
            
            # Check if email exists in the system
            email = form.cleaned_data['email']
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            if not User.objects.filter(email=email).exists():
                # Don't reveal if email exists or not for security
                messages.success(self.request, 
                    'If an account with that email exists, you will receive password reset instructions shortly.')
                return redirect('password_reset_done')
            
            response = super().form_valid(form)
            messages.success(self.request, 
                'Password reset email has been sent! Please check your inbox and spam folder.')
            return response
            
        except Exception as e:
            messages.error(self.request, 
                'Sorry, we encountered an issue sending the reset email. Please try again in a few minutes.')
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        """Handle form validation errors."""
        if form.errors.get('email'):
            messages.error(self.request, 'Please enter a valid email address.')
        else:
            messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)
    
    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        """Send a simple text email instead of HTML to avoid display issues."""
        try:
            subject = render_to_string(subject_template_name, context)
            subject = ''.join(subject.splitlines())  # Remove newlines
            
            # Use simple text content to avoid HTML display issues
            text_content = f"""
Hello,

You are receiving this email because you requested a password reset for your account at Afaa Elevate.

Please click the following link to reset your password:
{context['protocol']}://{context['domain']}/reset/{context['uid']}/{context['token']}/

This link will expire in 24 hours for security reasons.

If you did not request a password reset, please ignore this email.

Thanks,
The Afaa Elevate Team
"""
            
            from django.core.mail import send_mail
            send_mail(
                subject=subject,
                message=text_content,
                from_email=from_email,
                recipient_list=[to_email],
                fail_silently=False
            )
        except Exception as e:
            # Log the error for debugging but don't expose details to user
            # logger.error(f"Failed to send password reset email: {e}")
            raise Exception("Email delivery failed")

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'password_reset_confirm.html'
    
    def dispatch(self, *args, **kwargs):
        """Check if the reset link is valid before showing the form."""
        try:
            return super().dispatch(*args, **kwargs)
        except Exception as e:
            messages.error(self.request, 
                'This password reset link is invalid or has expired. Please request a new one.')
            return redirect('password_reset')
    
    def form_valid(self, form):
        """Handle successful password reset with automatic login."""
        try:
            # Call parent to validate and save the new password
            response = super().form_valid(form)
            
            # Get the user object
            user = form.user
            
            # Log the user in automatically
            auth_login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
            
            # Add success message
            messages.success(self.request, 
                'Your password has been successfully changed! You are now logged in.')
            
            # Redirect to dashboard
            return redirect('dashboard')
            
        except Exception as e:
            messages.error(self.request, 
                'An error occurred while changing your password. Please try again.')
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        """Handle form validation errors with specific messages."""
        if form.errors.get('new_password2'):
            messages.error(self.request, 'The passwords you entered do not match. Please try again.')
        elif form.errors.get('new_password1'):
            messages.error(self.request, 'Your password does not meet the security requirements.')
        else:
            messages.error(self.request, 'Please correct the errors below and try again.')
        
        return super().form_invalid(form)

def home_view(request):
    return render(request, 'main.html')

def signup_view(request):
    """Enhanced signup view with comprehensive error handling"""
    try:
        # Store referral code from URL in session if present
        referral_code = request.GET.get('ref') or request.GET.get('referral')
        if referral_code:
            request.session['referral_code'] = referral_code
        
        if request.method == 'POST':
            form = SignUpForm(request.POST)
            if form.is_valid():
                try:
                    with transaction.atomic():
                        user = form.save()
                        
                        # Get the profile that was created and updated by the form
                        profile = user.userprofile
                        
                        # Handle referral logic - only update referred_by if needed
                        referral_code_input = form.cleaned_data.get('referral_code')
                        if referral_code_input:
                            try:
                                # Find referrer by referral code or username
                                referrer_profile = UserProfile.objects.select_related('user').get(
                                    Q(referral_code__iexact=referral_code_input) | Q(user__username__iexact=referral_code_input)
                                )
                                referred_by = referrer_profile.user
                                # Only update referred_by field, don't overwrite other fields
                                profile.referred_by = referred_by
                                profile.save()
                            except UserProfile.DoesNotExist:
                                messages.warning(request, f"Referral code '{referral_code_input}' not found, but registration completed.")
                                referred_by = None
                        else:
                            referred_by = profile.referred_by

                        # Store Referral chain
                        level_1 = referred_by
                        level_2 = level_3 = None
                        if level_1 and hasattr(level_1, 'userprofile'):
                            level_2 = level_1.userprofile.referred_by
                            if level_2 and hasattr(level_2, 'userprofile'):
                                level_3 = level_2.userprofile.referred_by
                        
                        Referral.objects.create(referred=user, level_1=level_1, level_2=level_2, level_3=level_3)

                    # Login and redirect on success
                    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                    messages.success(request, "Successfully registered! Welcome.")
                    return redirect('dashboard')

                except IntegrityError as e:
                    # Handle database level integrity constraints
                    error_message = str(e).lower()
                    if 'email' in error_message or 'unique' in error_message:
                        messages.error(request, "This email address is already registered. Please use a different email or try to login.")
                    else:
                        messages.error(request, "A user with this username already exists. Please choose a different username.")
                except Exception as e:
                    # Catch any other unexpected errors
                    messages.error(request, f"An unexpected error occurred during registration: {e}")
                    # Optionally, log the error for debugging
                    # logger.error(f"Registration failed: {e}")
            else:
                messages.error(request, "Please fix the errors below.")
        else:
            form = SignUpForm()
        
        return render(request, 'signup.html', {'form': form})

    except Exception as e:
        # Comprehensive error handling for any view-level errors
        messages.error(request, "An error occurred while loading the signup page. Please try again.")
        # Log the error for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Signup view error: {e}")
        
        # Return a simple form in case of error
        form = SignUpForm()
        return render(request, 'signup.html', {'form': form})


@login_required
def user_dashboard(request):
    try:
        user = request.user

        # Gracefully get user profile
        try:
            user_profile = user.userprofile
        except UserProfile.DoesNotExist:
            # If profile doesn't exist, create one. This is a critical fallback.
            user_profile = UserProfile.objects.create(user=user)
            messages.info(request, "Your user profile was created.")

        # Site settings
        site_settings = SiteSetting.objects.first()

        # Courses unlocked by user's current plan
        my_courses = Course.objects.filter(plan__isnull=True) # Default to free courses
        if user_profile and user_profile.plan and user_profile.plan != 'NONE':
            try:
                user_plan_obj = Plan.objects.get(name__iexact=user_profile.plan)
                my_courses = Course.objects.filter(
                    Q(plan=user_plan_obj) | Q(plan__isnull=True)
                ).select_related('plan')
            except Plan.DoesNotExist:
                messages.warning(request, f"Your assigned plan '{user_profile.plan}' could not be found. Showing free courses only.")

        # Direct referrals
        direct_referrals = UserProfile.objects.filter(referred_by=user).select_related("user")
        
        # Plan-wise referral breakdown
        from .models import PLAN_CHOICES
        referrals_by_plan = {}
        plan_totals = {}
        
        for choice_code, choice_name in PLAN_CHOICES:
            if choice_code != 'NONE':
                plan_referrals = direct_referrals.filter(plan=choice_code)
                referrals_by_plan[choice_code] = plan_referrals
                plan_totals[choice_code] = plan_referrals.count()
        
        no_plan_referrals = direct_referrals.filter(plan='NONE')
        referrals_by_plan['NONE'] = no_plan_referrals
        plan_totals['NONE'] = no_plan_referrals.count()
        
        total_direct = direct_referrals.exclude(plan='NONE').count()

        # Commission earnings
        from datetime import datetime
        commissions = Commission.objects.filter(user=user)
        total_commission = commissions.aggregate(total=Sum("amount"))["total"] or 0
        
        current_month = datetime.now().month
        current_year = datetime.now().year
        monthly_commission = commissions.filter(
            created_at__month=current_month,
            created_at__year=current_year
        ).aggregate(total=Sum("amount"))["total"] or 0
        
        recent_commissions = commissions.order_by('-created_at')[:5]

        # Team rewards progress
        reward_progress = user_profile.get_reward_progress() if user_profile else []

        context = {
            "user": user,
            "user_profile": user_profile,
            "site_settings": site_settings,
            "my_courses": my_courses,
            "direct_referrals": direct_referrals,
            "total_direct": total_direct,
            "total_commission": total_commission,
            "monthly_commission": monthly_commission,
            "recent_commissions": recent_commissions,
            "reward_progress": reward_progress,
            "referrals_by_plan": referrals_by_plan,
            "plan_totals": plan_totals,
        }

        return render(request, "user_dashboard.html", context)

    except Exception as e:
        # Catch any unexpected error during dashboard loading
        messages.error(request, f"An error occurred while loading your dashboard. Please try again later.")
        # Log the error for debugging
        # logger.error(f"Dashboard error for user {request.user.id}: {e}")
        return redirect('home')


def courses_view(request):
    """Show all available courses regardless of plan"""
    plans = Plan.objects.all()
    courses = Course.objects.all().order_by('plan__name', 'title')  # Order by plan then title
    return render(request, 'courses.html', {'plans': plans, 'courses': courses})

@login_required
def buy_plan_view(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id)
    try:
        with transaction.atomic():
            # Create the UserPlan record
            UserPlan.objects.create(user=request.user, plan=plan)

            # Update the user's profile with the new plan
            profile = request.user.userprofile
            profile.plan = plan.name.upper()
            profile.save()

            # Trigger commission logic after the plan is successfully assigned
            handle_successful_referral(request.user)

        messages.success(request, f"You have successfully purchased the {plan.name}.")
    
    except UserProfile.DoesNotExist:
        messages.error(request, "Your user profile could not be found. Please contact support.")
    except Exception as e:
        # Catch any other unexpected errors during the purchase process
        messages.error(request, f"An unexpected error occurred while purchasing the plan: {e}")
        # logger.error(f"Plan purchase failed for user {request.user.id}: {e}")

    return redirect('dashboard')

@login_required
def manual_payment_view(request, plan_id=None):
    # ... (existing code is fine, as it just creates a pending record) ...
    plan = None
    if plan_id:
        plan = get_object_or_404(Plan, id=plan_id)

    if request.method == 'POST':
        proof_file = request.FILES.get('proof')
        amount = request.POST.get('amount') or (plan.price if plan else 0)
        Payment.objects.create(
            user=request.user,
            plan=plan,
            amount=amount,
            proof=proof_file,
            status='pending'
        )
        messages.success(request, "Your payment proof has been submitted and is pending approval.")
        return redirect('payments')

    return render(request, 'manual_payment.html', {'plan': plan})

def commission_view(request):
    try:
        from .referrals import get_user_commission_summary
        from .models import CommissionRate, Plan
        
        # Check if user is authenticated
        if request.user.is_authenticated:
            # Get user's commission summary
            commission_summary = get_user_commission_summary(request.user)
            
            # Gracefully get user's current plan
            try:
                user_plan = request.user.userprofile.plan
            except UserProfile.DoesNotExist:
                user_plan = 'NONE'
                messages.warning(request, "Your profile could not be found, so commission rates may not be accurate.")
        else:
            # For non-authenticated users, show default commission structure
            commission_summary = {
                'total_earned': 0,
                'pending_amount': 0,
                'paid_amount': 0,
                'level_1_count': 0,
                'level_2_count': 0,
                'level_3_count': 0,
            }
            user_plan = 'STANDARD'  # Show standard plan rates as example
        
        # Get commission structure for current user's plan
        commission_rates = []
        for plan in Plan.objects.all():
            try:
                rate = CommissionRate.objects.get(seller_plan=user_plan, sold_plan=plan, is_active=True)
                commission_rates.append({
                    'plan': plan,
                    'level_1': rate.level_1_percentage,
                    'level_2': rate.level_2_percentage, 
                    'level_3': rate.level_3_percentage,
                    'level_1_amount': (plan.price * rate.level_1_percentage) / 100,
                    'level_2_amount': (plan.price * rate.level_2_percentage) / 100,
                    'level_3_amount': (plan.price * rate.level_3_percentage) / 100,
                })
            except CommissionRate.DoesNotExist:
                # Fallback to default rates
                commission_rates.append({
                    'plan': plan,
                    'level_1': 40.00, 'level_2': 8.00, 'level_3': 2.00,
                    'level_1_amount': (plan.price * 40) / 100,
                    'level_2_amount': (plan.price * 8) / 100,
                    'level_3_amount': (plan.price * 2) / 100,
                })
        
        # Get recent commissions only for authenticated users
        if request.user.is_authenticated:
            recent_commissions = Commission.objects.filter(user=request.user).order_by('-created_at')[:10]
        else:
            recent_commissions = []  # Empty list for non-authenticated users
        
        context = {
            'user_plan': user_plan,
            'commission_summary': commission_summary,
            'commission_rates': commission_rates,
            'recent_commissions': recent_commissions,
            'is_authenticated': request.user.is_authenticated,
        }
        
        return render(request, 'commission.html', context)

    except Exception as e:
        messages.error(request, f"An error occurred while loading the commission details: {e}")
        # logger.error(f"Commission view error for user {request.user.id if request.user.is_authenticated else 'anonymous'}: {e}")
        if request.user.is_authenticated:
            return redirect('dashboard')
        else:
            return redirect('home')

def team_reward_view(request):
    return render(request, "team_reward.html")

@login_required
def payments_view(request):
    return render(request, "payments.html")
def privacy_policy_view(request):
    return render(request, "privacy_policy.html")
def terms_conditions_view(request):
    return render(request, "terms-conditions.html")


def login_view(request):
    """
    Custom login view with comprehensive error handling and referral support.
    This view is now cleaned up and does not contain debugging print statements.
    """
    from django.contrib.auth.forms import AuthenticationForm
    from django.contrib.auth import authenticate, login as auth_login
    
    # Check for referral code in URL parameters and store in session
    referral_code = request.GET.get('ref') or request.GET.get('referral')
    if referral_code:
        request.session['referral_code'] = referral_code
    
    # Redirect if already authenticated
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_active:
                    auth_login(request, user)
                    messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
                    return redirect('dashboard')
                else:
                    messages.error(request, 'Your account has been deactivated. Please contact support.')
            else:
                messages.error(request, 'Invalid username or password. Please try again.')
        else:
            # Add a generic error if the form is invalid, as the form itself will display field-specific errors.
            if not form.errors.get('__all__'):
                 messages.error(request, 'Please correct the errors below.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'registration/login.html', {'form': form})

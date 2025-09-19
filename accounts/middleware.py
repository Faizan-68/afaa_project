# accounts/middleware.py
from django.utils.deprecation import MiddlewareMixin
from django.urls import resolve
from urllib.parse import parse_qs, urlparse


class ReferralMiddleware(MiddlewareMixin):
    """
    Middleware to capture referral codes from URL parameters and store in session
    """
    
    def process_request(self, request):
        # Check if there's a referral code in URL parameters
        referral_code = request.GET.get('ref') or request.GET.get('referral')
        
        if referral_code:
            # Store referral code in session
            request.session['referral_code'] = referral_code
            print(f"🟢 MIDDLEWARE: Stored referral code in session: {referral_code}")
            print(f"🟢 MIDDLEWARE: Session ID: {request.session.session_key}")
        
        # Debug existing referral in session
        existing_referral = request.session.get('referral_code')
        if existing_referral:
            print(f"🔵 MIDDLEWARE: Existing referral in session: {existing_referral}")
        
        # Debug: Show current path when referral is in session
        if existing_referral:
            current_url = resolve(request.path_info)
            print(f"� MIDDLEWARE: Current path: {request.path}")
            print(f"� MIDDLEWARE: URL name: {current_url.url_name}")
        
        return None
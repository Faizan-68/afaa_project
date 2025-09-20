# accounts/middleware.py
from django.utils.deprecation import MiddlewareMixin


class ReferralMiddleware(MiddlewareMixin):
    """
    Middleware to capture referral codes from URL parameters and store in session
    """
    
    def process_request(self, request):
        try:
            # Ensure session is available
            if not hasattr(request, 'session'):
                return None
                
            # Check if there's a referral code in URL parameters
            referral_code = request.GET.get('ref') or request.GET.get('referral')
            
            if referral_code:
                # Store referral code in session
                request.session['referral_code'] = referral_code
                # Force session save to prevent loss
                request.session.modified = True
                
        except Exception as e:
            # Don't let referral middleware break the request
            # In production, log this error: logger.error(f"ReferralMiddleware error: {e}")
            pass
            
        return None
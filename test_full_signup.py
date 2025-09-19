#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'afaa_project.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile
from accounts.forms import SignUpForm
from accounts.views import signup_view
from django.test import RequestFactory
from django.contrib.messages.storage.fallback import FallbackStorage

# Test full signup view (which includes referral processing)
factory = RequestFactory()

# Test data with referral code
test_data = {
    'username': 'testuser4',
    'email': 'test4@example.com', 
    'password1': 'testpass123',
    'password2': 'testpass123',
    'mobile': '03009999999',
    'dob': '2000-12-25',
    'referral_code': 'faizan'  # existing user
}

print("Testing full signup view with referral code...")
print("=" * 60)

# Create mock request
request = factory.post('/signup/', test_data)
# Add message storage (required for views)
setattr(request, 'session', {})
messages = FallbackStorage(request)
setattr(request, '_messages', messages)

# Call the actual signup view
response = signup_view(request)

print(f"Response status: {response.status_code}")

# Check if user was created
try:
    user = User.objects.get(username='testuser4')
    profile = user.userprofile
    print(f"User created: {user.username}")
    print(f"Profile mobile: '{profile.mobile}'")
    print(f"Profile DOB: '{profile.dob}'")
    print(f"Profile referral_code: '{profile.referral_code}'")
    print(f"Profile referred_by: '{profile.referred_by}'")
except User.DoesNotExist:
    print("User was not created!")

print("Done!")
#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'afaa_project.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile
from allauth.socialaccount.models import SocialAccount, SocialApp
from allauth.socialaccount.signals import social_account_added
from django.test import RequestFactory

# Create a test Google user to simulate the signal
print("Testing social_account_added signal...")
print("=" * 50)

# Create test user
test_username = 'testgoogleuser123'
test_email = 'testgoogle@example.com'

# Delete if exists
User.objects.filter(username=test_username).delete()

# Create user
user = User.objects.create_user(username=test_username, email=test_email)
print(f"Created test user: {user.username}")

# Create social account for Google
social_account = SocialAccount.objects.create(
    user=user,
    provider='google',
    uid='123456789'
)
print(f"Created Google social account for: {user.username}")

# Check if profile was created
try:
    profile = user.userprofile
    print(f"Profile exists: referral_code = '{profile.referral_code}'")
except UserProfile.DoesNotExist:
    print("NO PROFILE CREATED - This is the problem!")

# Manually fire the signal to test
from django.test import RequestFactory
factory = RequestFactory()
request = factory.get('/')
request.session = {'referral_code': 'faizan'}

# Create mock sociallogin object
class MockSocialLogin:
    def __init__(self, user):
        self.user = user

sociallogin = MockSocialLogin(user)

# Import and call the signal handler directly
from accounts.signals import handle_social_signup
print("\nCalling signal handler directly...")
handle_social_signup(sender=None, request=request, sociallogin=sociallogin)

# Check profile again
try:
    profile = user.userprofile
    print(f"After signal: referral_code = '{profile.referral_code}'")
    print(f"After signal: referred_by = '{profile.referred_by}'")
except UserProfile.DoesNotExist:
    print("Still no profile - signal not working properly")

print("\nDone!")
#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'afaa_project.settings')
django.setup()

from accounts.models import UserProfile
from allauth.socialaccount.models import SocialAccount

# Fix existing Google users who don't have proper referral_code
print("Fixing existing Google users referral codes...")
print("=" * 50)

# Find Google users
google_accounts = SocialAccount.objects.filter(provider='google')
updated_count = 0

for social_account in google_accounts:
    user = social_account.user
    try:
        profile = user.userprofile
        
        # Check if referral_code is missing or not equal to username
        if not profile.referral_code or profile.referral_code != user.username:
            old_code = profile.referral_code
            profile.referral_code = user.username
            profile.save()
            updated_count += 1
            print(f"Updated Google user {user.username}: '{old_code}' -> '{profile.referral_code}'")
        else:
            print(f"Google user {user.username} already has correct referral_code: {profile.referral_code}")
            
    except UserProfile.DoesNotExist:
        # Create profile if it doesn't exist
        profile = UserProfile.objects.create(user=user, referral_code=user.username)
        updated_count += 1
        print(f"Created profile for Google user {user.username} with referral_code: {profile.referral_code}")

print(f"\nFixed {updated_count} Google user profiles.")
print("Done!")
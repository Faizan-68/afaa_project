#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'afaa_project.settings')
django.setup()

from accounts.models import UserProfile

# Check all UserProfiles
profiles = UserProfile.objects.all()
print(f'Total UserProfiles: {profiles.count()}')
print('=' * 50)

for profile in profiles:
    print(f'User: {profile.user.username}')
    print(f'Mobile: "{profile.mobile}"')
    print(f'DOB: {profile.dob}')
    print(f'Referral Code: "{profile.referral_code}"')
    print(f'Referred By: {profile.referred_by}')
    print('-' * 30)
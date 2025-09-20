#!/usr/bin/env python
import os
import django
import uuid

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'afaa_project.settings')
django.setup()

from accounts.models import UserProfile

# Update existing UserProfiles with missing referral codes
profiles = UserProfile.objects.all()
updated_count = 0

print(f'Updating {profiles.count()} UserProfiles...')
print('=' * 50)

for profile in profiles:
    # Generate referral code if missing
    if not profile.referral_code or profile.referral_code == 'None':
        profile.referral_code = f"{profile.user.username}_{str(uuid.uuid4())[:8]}"
        profile.save()
        updated_count += 1
        print(f'Updated {profile.user.username} with referral code: {profile.referral_code}')

print(f'\nUpdated {updated_count} profiles with referral codes.')
print('Done!')
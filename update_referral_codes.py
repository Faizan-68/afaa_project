#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'afaa_project.settings')
django.setup()

from accounts.models import UserProfile

# Update all UserProfiles to use username as referral code
profiles = UserProfile.objects.all()
updated_count = 0

print(f'Updating {profiles.count()} UserProfiles to use username as referral code...')
print('=' * 60)

for profile in profiles:
    # Set referral code as username (simple and clean)
    old_code = profile.referral_code
    profile.referral_code = profile.user.username
    profile.save()
    updated_count += 1
    print(f'Updated {profile.user.username}: "{old_code}" → "{profile.referral_code}"')

print(f'\nUpdated {updated_count} profiles.')
print('Now all users have their username as referral code!')
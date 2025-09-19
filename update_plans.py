

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'afaa_project.settings')
django.setup()

from accounts.models import UserProfile

# Update all users with BASIC plan to NONE (except if they have paid plans)
updated = UserProfile.objects.filter(plan='BASIC').update(plan='NONE')
print(f"✅ Updated {updated} users from BASIC to NONE plan")

# Show current plan distribution
from django.db.models import Count
plan_stats = UserProfile.objects.values('plan').annotate(count=Count('plan')).order_by('plan')

print("\n📊 Current Plan Distribution:")
for stat in plan_stats:
    print(f"   {stat['plan']}: {stat['count']} users")
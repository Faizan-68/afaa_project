# accounts/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile, Referral


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Create UserProfile when a new User is created via manual signup
    """
    if created:
        # Create profile for all new users
        profile, profile_created = UserProfile.objects.get_or_create(user=instance)
        if profile_created:
            profile.referral_code = instance.username
            profile.save()
            print(f"Profile created for {instance.username} with referral_code: {profile.referral_code}")
            
            # Handle referral assignment if there's a referral code in the request
            # This is handled in the signup_view, but we keep this as a fallback
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile, Plan, Commission

class Command(BaseCommand):
    help = 'Test plan upgrade from NONE to paid plan'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Testing Plan Upgrade from NONE'))
        
        try:
            # First reset user3 to NONE plan
            user3 = User.objects.get(username='user3')
            user3_profile = user3.userprofile
            
            self.stdout.write(f"Resetting user3 to NONE plan...")
            user3_profile.plan = 'NONE'
            user3_profile.save()
            
            self.stdout.write(f"user3 plan is now: {user3_profile.plan}")
            
            # Count current commissions
            current_count = Commission.objects.count()
            self.stdout.write(f"Current total commissions: {current_count}")
            
            # Now upgrade to Advance plan (this should trigger commission calculation)
            self.stdout.write(f"\n--- Upgrading user3 to Advance plan ---")
            user3_profile.plan = 'Advance'
            user3_profile.save()
            
            self.stdout.write(f"user3 plan is now: {user3_profile.plan}")
            
            # Check if new commissions were created
            new_count = Commission.objects.count()
            self.stdout.write(f"Total commissions after upgrade: {new_count}")
            self.stdout.write(f"New commissions created: {new_count - current_count}")
            
            # Show recent commissions for user3
            user3_commissions = Commission.objects.filter(referred_user=user3).order_by('-created_at')
            self.stdout.write(f"\nAll commissions for user3:")
            for commission in user3_commissions:
                self.stdout.write(f"  {commission.user.username} -> Rs.{commission.amount} (Level {commission.level}) - {commission.created_at}")
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))
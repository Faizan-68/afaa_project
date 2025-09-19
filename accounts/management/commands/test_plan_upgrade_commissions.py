from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile, Plan, Commission

class Command(BaseCommand):
    help = 'Test the new plan upgrade commission system'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Testing Plan Upgrade Commission System'))
        
        # First, let's check current commission data
        self.stdout.write(f"\nCurrent Commissions in database:")
        for commission in Commission.objects.all():
            self.stdout.write(f"  {commission.user.username} -> Rs.{commission.amount} from {commission.referred_user.username}")
        
        # Test scenario: Upgrade user3 from NONE to Standard plan
        try:
            user3 = User.objects.get(username='user3')
            user3_profile = user3.userprofile
            
            self.stdout.write(f"\nBefore upgrade:")
            self.stdout.write(f"  user3 plan: {user3_profile.plan}")
            self.stdout.write(f"  user3 referred by: {user3_profile.referred_by.username if user3_profile.referred_by else 'None'}")
            
            # Check referral chain
            if user3_profile.referred_by:
                user2_profile = user3_profile.referred_by.userprofile  
                self.stdout.write(f"  user2 plan: {user2_profile.plan}")
                self.stdout.write(f"  user2 referred by: {user2_profile.referred_by.username if user2_profile.referred_by else 'None'}")
                
                if user2_profile.referred_by:
                    user1_profile = user2_profile.referred_by.userprofile
                    self.stdout.write(f"  user1 plan: {user1_profile.plan}")
            
            # Simulate admin upgrading user3 from NONE to Standard
            self.stdout.write(f"\n--- Simulating admin upgrading user3 to Standard plan ---")
            
            # This should trigger commission calculation
            user3_profile.plan = 'Standard'
            user3_profile.save()
            
            self.stdout.write(f"After upgrade:")
            self.stdout.write(f"  user3 plan: {user3_profile.plan}")
            
            # Check new commissions
            self.stdout.write(f"\nNew Commissions after upgrade:")
            recent_commissions = Commission.objects.filter(referred_user=user3).order_by('-created_at')
            for commission in recent_commissions:
                self.stdout.write(f"  {commission.user.username} -> Rs.{commission.amount} from {commission.referred_user.username} (Level {commission.level})")
                
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('user3 not found. Please create sample users first.'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))
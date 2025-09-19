from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile, Commission

class Command(BaseCommand):
    help = 'Test admin panel simulation'

    def handle(self, *args, **options):
        self.stdout.write('Testing Admin Panel Commission Trigger')
        
        try:
            # Create a test user if doesn't exist
            user5, created = User.objects.get_or_create(
                username='user5',
                defaults={'email': 'user5@test.com', 'first_name': 'User5'}
            )
            
            # Get or create profile with referral
            try:
                profile5 = user5.userprofile
                # Ensure it has a referrer
                if not profile5.referred_by:
                    profile5.referred_by = User.objects.get(username='user1')
                    profile5.save()
                    self.stdout.write(f'Set user5 referred_by to user1')
                else:
                    self.stdout.write(f'user5 already referred by: {profile5.referred_by.username}')
            except:
                profile5 = UserProfile.objects.create(
                    user=user5,
                    plan='NONE',
                    referred_by=User.objects.get(username='user1')
                )
                self.stdout.write(f'Created new profile for: {user5.username}')
            
            # Reset to NONE for clean test
            profile5.plan = 'NONE'
            profile5.save()
            self.stdout.write(f'Reset user5 plan to NONE')
            self.stdout.write(f'user5 referred_by: {profile5.referred_by.username if profile5.referred_by else "None"}')
                
            # Count current commissions
            before_count = Commission.objects.count()
            self.stdout.write(f'Commissions before: {before_count}')
            
            # Simulate admin panel change - this should trigger our save method
            self.stdout.write(f'\n--- Simulating Admin Panel Update ---')
            self.stdout.write(f'Changing user5 plan from {profile5.plan} to STANDARD via admin...')
            
            # This is exactly what admin panel does
            profile5.plan = 'STANDARD'
            profile5.save()
            
            # Check if commission was created
            after_count = Commission.objects.count()
            self.stdout.write(f'Commissions after: {after_count}')
            self.stdout.write(f'New commissions: {after_count - before_count}')
            
            # Show the commission details
            new_commissions = Commission.objects.filter(referred_user=user5)
            for comm in new_commissions:
                self.stdout.write(f'Commission: {comm.user.username} gets Rs.{comm.amount} from {comm.referred_user.username}')
                
            self.stdout.write(self.style.SUCCESS('✅ Admin panel commission test complete'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))
            import traceback
            self.stdout.write(traceback.format_exc())
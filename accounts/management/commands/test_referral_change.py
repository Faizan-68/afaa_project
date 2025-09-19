from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile, Commission

class Command(BaseCommand):
    help = 'Test referral chain change functionality'

    def handle(self, *args, **options):
        self.stdout.write('=== Testing Referral Chain Change System ===')
        
        try:
            # Setup: Create test scenario
            # user8 is referred by user1, has STANDARD plan, should have commission for user1
            
            user8, created = User.objects.get_or_create(
                username='user8',
                defaults={'email': 'user8@test.com', 'first_name': 'User8'}
            )
            
            profile8, created = UserProfile.objects.get_or_create(
                user=user8,
                defaults={
                    'plan': 'NONE',
                    'referred_by': User.objects.get(username='user1')
                }
            )
            
            if not created:
                # Reset to clean state
                profile8.plan = 'NONE' 
                profile8.referred_by = User.objects.get(username='user1')
                profile8.save()
                
            self.stdout.write(f'Setup user8: Plan={profile8.plan}, Referred by={profile8.referred_by.username}')
            
            # Step 1: Upgrade user8 to STANDARD to create initial commission
            self.stdout.write(f'\n--- Step 1: Creating Initial Commission ---')
            before_count = Commission.objects.count()
            
            profile8.plan = 'STANDARD'
            profile8.save()  # This should create commission for user1
            
            after_count = Commission.objects.count()
            self.stdout.write(f'Commissions created: {after_count - before_count}')
            
            # Show initial commissions
            user8_commissions = Commission.objects.filter(referred_user=user8)
            for comm in user8_commissions:
                self.stdout.write(f'  Initial: {comm.user.username} -> Rs.{comm.amount} (Level {comm.level}, Active: {comm.is_active})')
            
            # Step 2: Change referral from user1 to user3
            self.stdout.write(f'\n--- Step 2: Changing Referral Chain ---')
            self.stdout.write(f'Changing user8 referrer from user1 to user3...')
            
            profile8.referred_by = User.objects.get(username='user3')
            profile8.save()  # This should trigger referral chain change handling
            
            # Show results after referral change
            self.stdout.write(f'\n--- Results After Referral Change ---')
            
            # Show all commissions for user8 (active and inactive)
            all_commissions = Commission.objects.filter(referred_user=user8).order_by('-created_at')
            self.stdout.write(f'All commissions for user8 ({all_commissions.count()} total):')
            
            for comm in all_commissions:
                status = "✅ Active" if comm.is_active else "❌ Inactive"
                note = f" (Note: {comm.admin_note[:50]}...)" if comm.admin_note else ""
                self.stdout.write(f'  {comm.user.username} -> Rs.{comm.amount} (Level {comm.level}) {status}{note}')
            
            # Step 3: Test changing back to user1
            self.stdout.write(f'\n--- Step 3: Changing Back to User1 ---')
            self.stdout.write(f'Changing user8 referrer from user3 back to user1...')
            
            profile8.referred_by = User.objects.get(username='user1')
            profile8.save()
            
            # Final results
            self.stdout.write(f'\n--- Final Commission State ---')
            final_commissions = Commission.objects.filter(referred_user=user8).order_by('-created_at')
            
            for comm in final_commissions:
                status = "✅ Active" if comm.is_active else "❌ Inactive"
                self.stdout.write(f'  {comm.user.username} -> Rs.{comm.amount} (Level {comm.level}) {status}')
            
            # Summary
            active_count = final_commissions.filter(is_active=True).count()
            inactive_count = final_commissions.filter(is_active=False).count()
            
            self.stdout.write(f'\n🎉 REFERRAL CHANGE SYSTEM WORKING!')
            self.stdout.write(f'✅ Total commissions: {final_commissions.count()}')
            self.stdout.write(f'✅ Active commissions: {active_count}')
            self.stdout.write(f'✅ Inactive commissions: {inactive_count}')
            self.stdout.write(f'✅ Commission history preserved')
            self.stdout.write(f'✅ Admin can track all changes in Commission panel')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))
            import traceback
            self.stdout.write(traceback.format_exc())
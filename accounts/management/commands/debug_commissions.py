from django.core.management.base import BaseCommand
from accounts.models import Commission, User, UserProfile, Payment
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Check commission data and debug issues'
    
    def handle(self, *args, **options):
        print('=== CHECKING COMMISSION DATA ===')
        
        users = User.objects.all()
        for user in users:
            commissions = Commission.objects.filter(user=user)
            referrals = UserProfile.objects.filter(referred_by=user)
            payments = Payment.objects.filter(user__in=[r.user for r in referrals], status='approved')
            
            print(f'User: {user.username}')
            print(f'  Referrals: {referrals.count()}')
            print(f'  Approved payments from referrals: {payments.count()}')
            print(f'  Commissions: {commissions.count()}')
            
            total = sum(c.amount for c in commissions)
            print(f'  Total Commission: Rs.{total}')
            
            if referrals.count() > 0 and commissions.count() == 0:
                print(f'  ❌ ISSUE: User has {referrals.count()} referrals but no commissions!')
                
            print('---')
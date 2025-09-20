from django.core.management.base import BaseCommand
from accounts.models import Payment, Plan, User
from accounts.referrals import handle_successful_payment

class Command(BaseCommand):
    help = 'Create sample payments to test commission system'
    
    def handle(self, *args, **options):
        print('=== CREATING SAMPLE PAYMENTS ===')
        
        # Get plans
        try:
            basic_plan = Plan.objects.get(name='Basic')
            standard_plan = Plan.objects.get(name='Standard')
        except Plan.DoesNotExist:
            print('Plans not found. Creating them first...')
            basic_plan = Plan.objects.create(name='Basic', price=500)
            standard_plan = Plan.objects.create(name='Standard', price=1000)
        
        # Get users
        try:
            user1 = User.objects.get(username='user1')  # Referrer
            user2 = User.objects.get(username='user2')  # Referred user 1
            user4 = User.objects.get(username='user4')  # Referred user 2
        except User.DoesNotExist:
            print('Required users not found!')
            return
        
        # Create payments for referred users
        payment1 = Payment.objects.create(
            user=user2,
            plan=basic_plan,
            amount=basic_plan.price,
            status='approved'  # Auto-approve
        )
        
        payment2 = Payment.objects.create(
            user=user4,
            plan=standard_plan,
            amount=standard_plan.price,
            status='approved'  # Auto-approve
        )
        
        print(f'Created payment for {user2.username}: Rs.{payment1.amount}')
        print(f'Created payment for {user4.username}: Rs.{payment2.amount}')
        
        # Trigger commission calculation manually
        print('\\n=== TRIGGERING COMMISSION CALCULATIONS ===')
        handle_successful_payment(payment1)
        handle_successful_payment(payment2)
        
        print('Sample payments created and commissions calculated!')
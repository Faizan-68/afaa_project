from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Plan, UserProfile, Payment
from accounts.referrals import handle_successful_payment
from decimal import Decimal

class Command(BaseCommand):
    help = 'Test commission calculation system with sample data'

    def handle(self, *args, **options):
        self.stdout.write('🧪 Testing Commission System...')
        
        # Create test users
        try:
            # Create referrer (Level 1)
            referrer = User.objects.create_user(
                username='referrer1',
                email='referrer1@test.com',
                password='testpass123',
                first_name='John',
                last_name='Referrer'
            )
            referrer.userprofile.plan = 'STANDARD'  # Standard plan user
            referrer.userprofile.save()
            
            # Create buyer (will be referred by referrer1)
            buyer = User.objects.create_user(
                username='buyer1',
                email='buyer1@test.com', 
                password='testpass123',
                first_name='Alice',
                last_name='Buyer'
            )
            buyer.userprofile.referred_by = referrer
            buyer.userprofile.save()
            
            self.stdout.write('✅ Test users created')
            
        except Exception as e:
            if 'UNIQUE constraint' in str(e):
                # Users already exist, get them
                referrer = User.objects.get(username='referrer1')
                buyer = User.objects.get(username='buyer1')
                self.stdout.write('✅ Using existing test users')
            else:
                self.stdout.write(f'❌ Error creating users: {e}')
                return

        # Get Pro plan for testing
        try:
            pro_plan = Plan.objects.get(name__icontains='pro')
        except Plan.DoesNotExist:
            self.stdout.write('❌ Pro plan not found')
            return

        # Create a test payment (buyer purchases Pro plan)
        payment = Payment.objects.create(
            user=buyer,
            plan=pro_plan,
            amount=pro_plan.price,
            status='approved'
        )
        
        self.stdout.write(f'✅ Payment created: {buyer.username} bought {pro_plan.name} for Rs.{pro_plan.price}')
        
        # Calculate commissions
        try:
            handle_successful_payment(payment)
            self.stdout.write('✅ Commission calculation completed')
            
            # Check results
            from accounts.models import Commission
            commissions = Commission.objects.filter(payment=payment)
            
            self.stdout.write(f'\n📊 Commission Results:')
            total_commission = Decimal('0.00')
            
            for commission in commissions:
                self.stdout.write(
                    f'   Level {commission.level}: {commission.user.username} earns '
                    f'Rs.{commission.amount} ({commission.percentage_rate}%)'
                )
                total_commission += commission.amount
            
            self.stdout.write(f'\n💰 Total commissions distributed: Rs.{total_commission}')
            self.stdout.write(f'🎯 Plan price: Rs.{pro_plan.price}')
            self.stdout.write(f'📈 Commission percentage: {(total_commission/pro_plan.price*100):.1f}%')
            
        except Exception as e:
            self.stdout.write(f'❌ Commission calculation error: {e}')
            import traceback
            traceback.print_exc()

        self.stdout.write('\n✨ Commission system test completed!')
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Plan, UserProfile, Payment, Commission
from accounts.referrals import handle_successful_payment
from decimal import Decimal
import random

class Command(BaseCommand):
    help = 'Create sample commission data for dashboard testing'

    def handle(self, *args, **options):
        self.stdout.write('🎯 Creating sample commission data...')
        
        # Get or create admin user to test with
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@test.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            admin_user.userprofile.plan = 'PRO'
            admin_user.userprofile.save()
            self.stdout.write('✅ Admin user created with PRO plan')
        else:
            admin_user.userprofile.plan = 'PRO'
            admin_user.userprofile.save()
            self.stdout.write('✅ Admin user updated to PRO plan')
        
        # Create some referrals for admin
        sample_buyers = [
            {'username': 'buyer_alice', 'name': 'Alice Johnson'},
            {'username': 'buyer_bob', 'name': 'Bob Smith'}, 
            {'username': 'buyer_carol', 'name': 'Carol Wilson'},
        ]
        
        plans = list(Plan.objects.all())
        
        for i, buyer_data in enumerate(sample_buyers):
            # Create buyer if doesn't exist
            buyer, created = User.objects.get_or_create(
                username=buyer_data['username'],
                defaults={
                    'email': f'{buyer_data["username"]}@test.com',
                    'first_name': buyer_data['name'].split()[0],
                    'last_name': buyer_data['name'].split()[1],
                }
            )
            
            if created:
                buyer.set_password('test123')
                buyer.save()
            
            # Set referral relationship
            buyer.userprofile.referred_by = admin_user
            buyer.userprofile.save()
            
            # Create payment for random plan
            plan = random.choice(plans)
            payment, created = Payment.objects.get_or_create(
                user=buyer,
                plan=plan,
                defaults={
                    'amount': plan.price,
                    'status': 'approved'
                }
            )
            
            if created:
                # Calculate commission
                handle_successful_payment(payment)
                self.stdout.write(f'✅ Created commission for {buyer.first_name} buying {plan.name}')
        
        # Summary
        total_commissions = Commission.objects.filter(user=admin_user).count()
        total_amount = sum(c.amount for c in Commission.objects.filter(user=admin_user))
        
        self.stdout.write(f'\n📊 Summary for admin user:')
        self.stdout.write(f'   Total Commission Transactions: {total_commissions}')
        self.stdout.write(f'   Total Commission Amount: Rs.{total_amount}')
        self.stdout.write(f'   Login with: admin / admin123')
        self.stdout.write('\n✨ Sample data created successfully!')
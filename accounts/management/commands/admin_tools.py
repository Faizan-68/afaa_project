"""
Admin Management Commands and Quick Actions
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile, Payment, Plan, UserPlan
from accounts.referrals import handle_successful_referral

class Command(BaseCommand):
    help = 'Admin management utilities'
    
    def add_arguments(self, parser):
        parser.add_argument('--action', type=str, help='Action to perform')
        parser.add_argument('--user', type=str, help='Username')
        parser.add_argument('--plan', type=str, help='Plan name')
    
    def handle(self, *args, **options):
        action = options['action']
        
        if action == 'list_pending_payments':
            self.list_pending_payments()
        elif action == 'approve_user_payment':
            self.approve_user_payment(options['user'])
        elif action == 'assign_plan':
            self.assign_plan(options['user'], options['plan'])
        elif action == 'show_stats':
            self.show_stats()
    
    def list_pending_payments(self):
        """List all pending payments"""
        payments = Payment.objects.filter(status='pending').order_by('-created_at')
        
        self.stdout.write("📋 PENDING PAYMENTS:")
        self.stdout.write("=" * 50)
        
        for payment in payments:
            self.stdout.write(
                f"👤 {payment.user.username} | "
                f"💰 Rs. {payment.amount} | "
                f"📦 {payment.plan.name if payment.plan else 'No Plan'} | "
                f"📅 {payment.created_at.strftime('%Y-%m-%d')}"
            )
        
        if not payments:
            self.stdout.write("✅ No pending payments!")
    
    def approve_user_payment(self, username):
        """Approve payment for specific user"""
        try:
            user = User.objects.get(username=username)
            payment = Payment.objects.filter(user=user, status='pending').first()
            
            if payment:
                payment.status = 'approved'
                payment.save()
                
                # Create UserPlan
                UserPlan.objects.get_or_create(user=user, plan=payment.plan)
                
                # Update profile
                profile = user.userprofile
                profile.plan = payment.plan.name.upper()
                profile.save()
                
                # Handle referrals
                handle_successful_referral(user)
                
                self.stdout.write(f"✅ Payment approved for {username}")
            else:
                self.stdout.write(f"❌ No pending payment found for {username}")
                
        except User.DoesNotExist:
            self.stdout.write(f"❌ User {username} not found")
    
    def assign_plan(self, username, plan_name):
        """Assign plan directly to user"""
        try:
            user = User.objects.get(username=username)
            plan = Plan.objects.get(name__iexact=plan_name)
            
            # Create or update UserPlan
            user_plan, created = UserPlan.objects.get_or_create(
                user=user, 
                plan=plan
            )
            
            # Update profile
            profile = user.userprofile
            profile.plan = plan.name.upper()
            profile.save()
            
            # Handle referrals
            handle_successful_referral(user)
            
            action = "assigned" if created else "updated"
            self.stdout.write(f"✅ Plan {plan.name} {action} to {username}")
            
        except User.DoesNotExist:
            self.stdout.write(f"❌ User {username} not found")
        except Plan.DoesNotExist:
            self.stdout.write(f"❌ Plan {plan_name} not found")
    
    def show_stats(self):
        """Show system statistics"""
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        pending_payments = Payment.objects.filter(status='pending').count()
        approved_payments = Payment.objects.filter(status='approved').count()
        
        self.stdout.write("📊 SYSTEM STATISTICS:")
        self.stdout.write("=" * 50)
        self.stdout.write(f"👥 Total Users: {total_users}")
        self.stdout.write(f"✅ Active Users: {active_users}")
        self.stdout.write(f"⏳ Pending Payments: {pending_payments}")
        self.stdout.write(f"✅ Approved Payments: {approved_payments}")
        
        # Plan distribution
        for choice in UserProfile.PLAN_CHOICES:
            count = UserProfile.objects.filter(plan=choice[0]).count()
            self.stdout.write(f"📦 {choice[1]} Plan: {count}")
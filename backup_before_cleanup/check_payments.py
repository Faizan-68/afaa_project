from django.core.management.base import BaseCommand
from accounts.models import Payment, User

class Command(BaseCommand):
    help = 'Check payment data'
    
    def handle(self, *args, **options):
        print('=== CHECKING PAYMENT DATA ===')
        
        payments = Payment.objects.all()
        for payment in payments:
            plan_name = payment.plan.name if payment.plan else "None"
            print(f'Payment: {payment.user.username}, Plan: {plan_name}, Status: {payment.status}, Amount: Rs.{payment.amount}')
            
        print(f'\nTotal payments: {payments.count()}')
        approved_payments = Payment.objects.filter(status='approved')
        print(f'Approved payments: {approved_payments.count()}')
from django.core.management.base import BaseCommand
from accounts.models import CommissionRate, Plan
from decimal import Decimal

class Command(BaseCommand):
    help = 'Populate commission rates based on the provided structure'

    def handle(self, *args, **options):
        self.stdout.write('Setting up commission rate structure...')
        
        # Get all plans
        try:
            basic_plan = Plan.objects.get(name__icontains='basic')
            standard_plan = Plan.objects.get(name__icontains='standard') 
            advance_plan = Plan.objects.get(name__icontains='advance')
            pro_plan = Plan.objects.get(name__icontains='pro')
        except Plan.DoesNotExist:
            self.stdout.write(self.style.ERROR('Plans not found. Please create plans first.'))
            return

        # Commission structure as per your requirements
        commission_structure = [
            # BASIC PLAN USER selling different plans
            {'seller': 'BASIC', 'sold': basic_plan, 'l1': Decimal('40.00'), 'l2': Decimal('8.00'), 'l3': Decimal('2.00')},
            {'seller': 'BASIC', 'sold': standard_plan, 'l1': Decimal('42.00'), 'l2': Decimal('8.00'), 'l3': Decimal('2.00')},
            {'seller': 'BASIC', 'sold': advance_plan, 'l1': Decimal('44.00'), 'l2': Decimal('8.00'), 'l3': Decimal('2.00')},
            {'seller': 'BASIC', 'sold': pro_plan, 'l1': Decimal('46.00'), 'l2': Decimal('8.00'), 'l3': Decimal('2.00')},
            
            # STANDARD PLAN USER selling different plans  
            {'seller': 'STANDARD', 'sold': basic_plan, 'l1': Decimal('40.00'), 'l2': Decimal('8.00'), 'l3': Decimal('2.00')},
            {'seller': 'STANDARD', 'sold': standard_plan, 'l1': Decimal('45.00'), 'l2': Decimal('8.00'), 'l3': Decimal('2.00')},
            {'seller': 'STANDARD', 'sold': advance_plan, 'l1': Decimal('47.00'), 'l2': Decimal('8.00'), 'l3': Decimal('2.00')},
            {'seller': 'STANDARD', 'sold': pro_plan, 'l1': Decimal('50.00'), 'l2': Decimal('8.00'), 'l3': Decimal('2.00')},
            
            # ADVANCE PLAN USER selling different plans
            {'seller': 'ADVANCE', 'sold': basic_plan, 'l1': Decimal('42.00'), 'l2': Decimal('8.00'), 'l3': Decimal('2.00')},
            {'seller': 'ADVANCE', 'sold': standard_plan, 'l1': Decimal('48.00'), 'l2': Decimal('8.00'), 'l3': Decimal('2.00')},
            {'seller': 'ADVANCE', 'sold': advance_plan, 'l1': Decimal('52.00'), 'l2': Decimal('8.00'), 'l3': Decimal('2.00')},
            {'seller': 'ADVANCE', 'sold': pro_plan, 'l1': Decimal('55.00'), 'l2': Decimal('8.00'), 'l3': Decimal('2.00')},
            
            # PRO PLAN USER selling different plans
            {'seller': 'PRO', 'sold': basic_plan, 'l1': Decimal('45.00'), 'l2': Decimal('8.00'), 'l3': Decimal('2.00')},
            {'seller': 'PRO', 'sold': standard_plan, 'l1': Decimal('52.00'), 'l2': Decimal('8.00'), 'l3': Decimal('2.00')},
            {'seller': 'PRO', 'sold': advance_plan, 'l1': Decimal('56.00'), 'l2': Decimal('8.00'), 'l3': Decimal('2.00')},
            {'seller': 'PRO', 'sold': pro_plan, 'l1': Decimal('60.00'), 'l2': Decimal('8.00'), 'l3': Decimal('2.00')},
        ]

        created_count = 0
        updated_count = 0

        for rate_data in commission_structure:
            commission_rate, created = CommissionRate.objects.get_or_create(
                seller_plan=rate_data['seller'],
                sold_plan=rate_data['sold'],
                defaults={
                    'level_1_percentage': rate_data['l1'],
                    'level_2_percentage': rate_data['l2'],
                    'level_3_percentage': rate_data['l3'],
                    'is_active': True
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(f'✅ Created: {rate_data["seller"]} selling {rate_data["sold"].name}')
            else:
                # Update existing rates
                commission_rate.level_1_percentage = rate_data['l1']
                commission_rate.level_2_percentage = rate_data['l2'] 
                commission_rate.level_3_percentage = rate_data['l3']
                commission_rate.is_active = True
                commission_rate.save()
                updated_count += 1
                self.stdout.write(f'🔄 Updated: {rate_data["seller"]} selling {rate_data["sold"].name}')

        self.stdout.write(
            self.style.SUCCESS(
                f'Commission rates setup complete! Created: {created_count}, Updated: {updated_count}'
            )
        )
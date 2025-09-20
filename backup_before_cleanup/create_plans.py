# Create default plans for the system
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'afaa_project.settings')
django.setup()

from accounts.models import Plan

# Create default plans
plans_data = [
    {"name": "BASIC", "description": "Basic plan with limited features", "price": 500.00},
    {"name": "STANDARD", "description": "Standard plan with more features", "price": 1500.00},
    {"name": "ADVANCE", "description": "Advanced plan with premium features", "price": 3000.00},
    {"name": "PRO", "description": "Professional plan with all features", "price": 5000.00},
]

created_count = 0
for plan_data in plans_data:
    plan, created = Plan.objects.get_or_create(
        name=plan_data["name"],
        defaults={
            "description": plan_data["description"],
            "price": plan_data["price"]
        }
    )
    if created:
        created_count += 1
        print(f"✅ Created plan: {plan.name} - Rs {plan.price}")
    else:
        print(f"📝 Plan already exists: {plan.name}")

print(f"\n🎉 Total plans created: {created_count}")
print(f"📊 Total plans in database: {Plan.objects.count()}")

# Show all plans
print("\n📋 All Plans:")
for plan in Plan.objects.all():
    print(f"   {plan.name}: Rs {plan.price} - {plan.description}")
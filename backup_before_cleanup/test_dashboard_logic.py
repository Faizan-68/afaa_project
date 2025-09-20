# Test dashboard course display logic
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'afaa_project.settings')
django.setup()

from accounts.models import Course, Plan, UserProfile
from django.contrib.auth.models import User
from django.db.models import Q

print("🧪 Testing Dashboard Course Display Logic\n")

# Show all users and their plans
print("📋 Current Users and Plans:")
for user in User.objects.all():
    try:
        plan = user.userprofile.plan
        print(f"  👤 {user.username}: {plan}")
    except:
        print(f"  👤 {user.username}: No Profile")

print("\n📚 Available Courses:")
for course in Course.objects.all():
    plan_name = course.plan.name if course.plan else "FREE"
    print(f"  📖 {course.title} → {plan_name}")

print("\n🔍 Testing Course Access by Plan:")

# Test each plan type
test_plans = ['NONE', 'BASIC', 'STANDARD', 'ADVANCE', 'PRO']

for test_plan in test_plans:
    print(f"\n  🏷️  {test_plan} Plan Access:")
    
    if test_plan == 'NONE':
        # Show only free courses
        courses = Course.objects.filter(plan__isnull=True)
    else:
        try:
            plan_obj = Plan.objects.get(name=test_plan)
            # Show plan courses + free courses
            courses = Course.objects.filter(
                Q(plan=plan_obj) | Q(plan__isnull=True)
            )
        except Plan.DoesNotExist:
            courses = Course.objects.filter(plan__isnull=True)
    
    if courses.exists():
        for course in courses:
            course_type = "FREE" if not course.plan else course.plan.name
            print(f"    ✅ {course.title} ({course_type})")
    else:
        print(f"    ❌ No courses available")

print(f"\n✨ Dashboard logic test completed!")

# Create a test user with different plan to verify
print(f"\n🔄 Testing with sample user...")
try:
    test_user = User.objects.get(username='testuser')
except User.DoesNotExist:
    test_user = User.objects.create_user('testuser', 'test@example.com', 'password')
    
profile = test_user.userprofile
profile.plan = 'STANDARD'
profile.save()

print(f"👤 Test user '{test_user.username}' has '{profile.plan}' plan")
standard_plan = Plan.objects.get(name='STANDARD')
test_courses = Course.objects.filter(
    Q(plan=standard_plan) | Q(plan__isnull=True)
)

print("📚 Courses available to STANDARD user:")
for course in test_courses:
    course_type = "FREE" if not course.plan else course.plan.name
    print(f"  ✅ {course.title} ({course_type})")
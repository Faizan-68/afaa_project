# Test course link functionality
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'afaa_project.settings')
django.setup()

from accounts.models import Course, Plan

# Get a plan
basic_plan = Plan.objects.get(name='BASIC')

# Update an existing course with a course link
course = Course.objects.get(title='Introduction to Digital Marketing')
course.course_link = 'https://learn.afaa-elevate.com/digital-marketing-101'
course.save()

print(f"✅ Updated course: {course.title}")
print(f"🔗 Course link: {course.course_link}")

# Show all courses with their links
print("\n📚 All Courses with Links:")
for course in Course.objects.all():
    link_status = "🔗 " + course.course_link if course.course_link else "❌ No Link"
    print(f"  {course.title}: {link_status}")
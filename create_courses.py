# Create sample courses for testing
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'afaa_project.settings')
django.setup()

from accounts.models import Course, Plan

# Get plans
basic_plan = Plan.objects.get(name='BASIC')
standard_plan = Plan.objects.get(name='STANDARD')
advance_plan = Plan.objects.get(name='ADVANCE')
pro_plan = Plan.objects.get(name='PRO')

# Create sample courses
courses_data = [
    {
        "title": "Introduction to Digital Marketing",
        "description": "Learn the basics of digital marketing including SEO, social media, and content marketing.",
        "plan": basic_plan,
        "course_link": "https://example.com/digital-marketing-course"
    },
    {
        "title": "Advanced Web Development",
        "description": "Master modern web development with React, Node.js, and advanced JavaScript concepts.",
        "plan": standard_plan,
        "course_link": "https://example.com/web-development-course"
    },
    {
        "title": "Data Science & Machine Learning",
        "description": "Complete guide to data science, Python, machine learning algorithms, and AI implementation.",
        "plan": advance_plan,
        "course_link": "https://example.com/data-science-course"
    },
    {
        "title": "Full Stack Business Development",
        "description": "Comprehensive business development course covering all aspects of entrepreneurship and scaling.",
        "plan": pro_plan,
        "course_link": "https://example.com/business-development-course"
    },
    {
        "title": "Free Resource Library",
        "description": "Access to basic resources and free learning materials.",
        "plan": None,  # No plan required
        "course_link": "https://example.com/free-resources"
    }
]

created_count = 0
for course_data in courses_data:
    course, created = Course.objects.get_or_create(
        title=course_data["title"],
        defaults=course_data
    )
    if created:
        created_count += 1
        plan_name = course.plan.name if course.plan else "No Plan"
        print(f"✅ Created course: {course.title} ({plan_name})")
    else:
        print(f"📝 Course already exists: {course.title}")

print(f"\n🎉 Total courses created: {created_count}")
print(f"📊 Total courses in database: {Course.objects.count()}")

# Show courses by plan
print("\n📋 Courses by Plan:")
for plan in Plan.objects.all():
    courses = Course.objects.filter(plan=plan)
    print(f"\n   {plan.name} (Rs {plan.price}):")
    for course in courses:
        print(f"      - {course.title}")

# Show courses without plan
free_courses = Course.objects.filter(plan=None)
if free_courses.exists():
    print(f"\n   FREE COURSES:")
    for course in free_courses:
        print(f"      - {course.title}")
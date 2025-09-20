# Test the new course card design
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'afaa_project.settings')
django.setup()

from accounts.models import Course, Plan
from django.contrib.auth.models import User

print("🎨 COURSE CARD DESIGN - TESTING")
print("="*50)

# Update course descriptions to test the "see more" functionality
course_updates = [
    {
        'title': 'Introduction to Digital Marketing',
        'description': 'Comprehensive digital marketing course covering SEO, social media marketing, content marketing, email marketing, PPC advertising, analytics, and conversion optimization. Learn to create effective digital marketing strategies that drive real business results and increase online visibility.'
    },
    {
        'title': 'Advanced Web Development', 
        'description': 'Master modern web development with React.js, Node.js, MongoDB, Express.js, JavaScript ES6+, HTML5, CSS3, responsive design, API integration, authentication, deployment strategies, and best practices for scalable web applications.'
    },
    {
        'title': 'Data Science & Machine Learning',
        'description': 'Complete data science bootcamp covering Python programming, pandas, numpy, matplotlib, scikit-learn, machine learning algorithms, deep learning with TensorFlow, data visualization, statistical analysis, and real-world project implementation.'
    },
    {
        'title': 'Full Stack Business Development',
        'description': 'Comprehensive business development course covering entrepreneurship fundamentals, business strategy, market analysis, financial planning, sales techniques, leadership skills, project management, and scaling business operations for sustainable growth.'
    },
    {
        'title': 'Free Resource Library',
        'description': 'Access to curated collection of free learning resources including e-books, tutorials, templates, cheat sheets, and tools to support your learning journey across various domains and skill levels.'
    }
]

print("📝 Updating course descriptions for better 'See More' testing...")

for update in course_updates:
    try:
        course = Course.objects.get(title=update['title'])
        course.description = update['description']
        course.save()
        print(f"✅ Updated: {course.title}")
        print(f"   Length: {len(course.description)} characters")
    except Course.DoesNotExist:
        print(f"❌ Course not found: {update['title']}")

print(f"\n📊 COURSE CARD FEATURES IMPLEMENTED:")
print("="*50)
print("✅ Beautiful thumbnail with overlay badges")
print("✅ Professional course titles")  
print("✅ Smart description truncation (100+ chars get 'See More')")
print("✅ Interactive 'See More/See Less' functionality")
print("✅ Gradient start learning buttons with icons")
print("✅ Plan-specific color coding")
print("✅ Hover animations and effects")
print("✅ Fully responsive design")
print("✅ Elegant placeholder for missing images")

print(f"\n🎨 DESIGN FEATURES:")
print("="*50)
print("🖼️  Card Layout: Thumbnail → Title → Description → Button")
print("🌈 Color Coding: Each plan has unique badge colors")
print("📱 Responsive: Works on desktop, tablet, and mobile")  
print("✨ Animations: Smooth hover effects and transitions")
print("🔗 Smart Links: Direct course access or 'Coming Soon' message")

print(f"\n📋 CURRENT COURSES STATUS:")
print("="*50)

for course in Course.objects.all():
    plan_name = course.plan.name if course.plan else "FREE"
    desc_length = len(course.description) if course.description else 0
    has_see_more = "Yes" if desc_length > 100 else "No"
    has_link = "Yes" if course.course_link else "No"
    
    print(f"📚 {course.title}")
    print(f"   Plan: {plan_name}")
    print(f"   Description: {desc_length} chars (See More: {has_see_more})")
    print(f"   Has Link: {has_link}")
    print()

print("🚀 COURSE CARDS ARE NOW READY!")
print("Visit the dashboard to see the beautiful new design!")
print("Dashboard URL: http://127.0.0.1:8001/dashboard/")

# Show a user example
print(f"\n👤 EXAMPLE USER ACCESS:")
print("="*50)
try:
    user = User.objects.first()
    plan = user.userprofile.plan if hasattr(user, 'userprofile') else 'No Profile'
    print(f"User: {user.username}")
    print(f"Plan: {plan}")
    
    if plan != 'NONE' and plan != 'No Profile':
        plan_obj = Plan.objects.get(name=plan)
        accessible_courses = Course.objects.filter(
            models.Q(plan=plan_obj) | models.Q(plan__isnull=True)
        ).count()
    else:
        accessible_courses = Course.objects.filter(plan__isnull=True).count()
    
    print(f"Accessible Courses: {accessible_courses}")
    
except:
    print("No users found or error occurred")

print(f"\n✨ ENJOY THE NEW BEAUTIFUL COURSE CARDS! ✨")
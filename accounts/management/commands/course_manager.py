from django.core.management.base import BaseCommand
from accounts.models import Plan, Course, UserProfile
from django.db.models import Count

class Command(BaseCommand):
    help = 'Manage courses and plans - create, list, and analyze data'

    def add_arguments(self, parser):
        parser.add_argument('action', choices=['list', 'stats', 'create_plan', 'create_course'])
        parser.add_argument('--name', type=str, help='Name for plan or course')
        parser.add_argument('--price', type=float, help='Price for plan')
        parser.add_argument('--description', type=str, help='Description')
        parser.add_argument('--plan', type=str, help='Plan name for course')

    def handle(self, *args, **options):
        action = options['action']
        
        if action == 'list':
            self.list_all()
        elif action == 'stats':
            self.show_stats()
        elif action == 'create_plan':
            self.create_plan(options)
        elif action == 'create_course':
            self.create_course(options)

    def list_all(self):
        self.stdout.write(self.style.SUCCESS('\n📋 PLANS:'))
        for plan in Plan.objects.all():
            course_count = plan.course_set.count()
            user_count = UserProfile.objects.filter(plan=plan.name).count()
            self.stdout.write(f"  {plan.name}: Rs {plan.price} | {course_count} courses | {user_count} users")
        
        self.stdout.write(self.style.SUCCESS('\n📚 COURSES:'))
        for course in Course.objects.all():
            plan_name = course.plan.name if course.plan else "No Plan"
            self.stdout.write(f"  {course.title} → {plan_name}")

    def show_stats(self):
        total_plans = Plan.objects.count()
        total_courses = Course.objects.count()
        total_users = UserProfile.objects.count()
        
        self.stdout.write(self.style.SUCCESS('\n📊 STATISTICS:'))
        self.stdout.write(f"  Total Plans: {total_plans}")
        self.stdout.write(f"  Total Courses: {total_courses}")
        self.stdout.write(f"  Total Users: {total_users}")
        
        # User distribution by plan
        self.stdout.write(self.style.SUCCESS('\n👥 USER DISTRIBUTION:'))
        plan_stats = UserProfile.objects.values('plan').annotate(count=Count('plan')).order_by('plan')
        for stat in plan_stats:
            self.stdout.write(f"  {stat['plan']}: {stat['count']} users")
        
        # Courses per plan
        self.stdout.write(self.style.SUCCESS('\n📚 COURSES PER PLAN:'))
        for plan in Plan.objects.all():
            count = plan.course_set.count()
            self.stdout.write(f"  {plan.name}: {count} courses")
        
        free_courses = Course.objects.filter(plan=None).count()
        if free_courses > 0:
            self.stdout.write(f"  FREE: {free_courses} courses")

    def create_plan(self, options):
        if not options['name'] or not options['price']:
            self.stdout.write(self.style.ERROR('Please provide --name and --price'))
            return
        
        plan, created = Plan.objects.get_or_create(
            name=options['name'],
            defaults={
                'price': options['price'],
                'description': options.get('description', f"{options['name']} plan")
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f"✅ Created plan: {plan.name} - Rs {plan.price}"))
        else:
            self.stdout.write(self.style.WARNING(f"Plan {plan.name} already exists"))

    def create_course(self, options):
        if not options['name']:
            self.stdout.write(self.style.ERROR('Please provide --name'))
            return
        
        plan = None
        if options['plan']:
            try:
                plan = Plan.objects.get(name=options['plan'])
            except Plan.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Plan '{options['plan']}' not found"))
                return
        
        course, created = Course.objects.get_or_create(
            title=options['name'],
            defaults={
                'description': options.get('description', f"{options['name']} course"),
                'plan': plan
            }
        )
        
        if created:
            plan_name = plan.name if plan else "No Plan"
            self.stdout.write(self.style.SUCCESS(f"✅ Created course: {course.title} ({plan_name})"))
        else:
            self.stdout.write(self.style.WARNING(f"Course {course.title} already exists"))
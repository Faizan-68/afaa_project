# accounts/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Plans (product)
class Plan(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

# each course can be linked to a Plan
class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(default="No description provided")
    plan = models.ForeignKey(Plan, null=True, blank=True, on_delete=models.SET_NULL)
    thumbnail = models.ImageField(upload_to='courses_thumbnails/', null=True, blank=True)
    course_link = models.URLField(blank=True, null=True, help_text="Add the actual course learning link here")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class UserPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    purchase_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.plan.name}"

# Site settings editable from admin
class SiteSetting(models.Model):
    site_name = models.CharField(max_length=200, default='Afaa Elevate')
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    facebook = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    youtube = models.URLField(blank=True, null=True)
    whatsapp = models.CharField(max_length=50, blank=True, null=True)
    whatsapp_channel = models.URLField(blank=True, null=True)

    @property
    def whatsapp_number(self):
        if not self.whatsapp:
            return ''
        return "".join(filter(str.isdigit, self.whatsapp))

    def __str__(self):
        return "Site settings"

# Profile to extend Django User
PLAN_CHOICES = [
    ('NONE', 'None'),
    ('BASIC', 'Basic'),
    ('STANDARD', 'Standard'),
    ('ADVANCE', 'Advance'),
    ('PRO', 'Pro'),
]

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='NONE')
    referred_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='direct_referrals')
    mobile = models.CharField(max_length=30, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    referral_code = models.CharField(max_length=150, blank=True, null=True)

    def __str__(self):
        return self.user.username

    def total_direct_referrals(self):
        # count of profiles referred directly by this user
        return UserProfile.objects.filter(referred_by=self.user).count()
    
    def get_referral_counts_by_plan(self):
        """Get count of referrals by plan type"""
        referrals = UserProfile.objects.filter(referred_by=self.user)
        counts = {
            'BASIC': referrals.filter(plan='BASIC').count(),
            'STANDARD': referrals.filter(plan='STANDARD').count(), 
            'ADVANCE': referrals.filter(plan='ADVANCE').count(),
            'PRO': referrals.filter(plan='PRO').count(),
            'NONE': referrals.filter(plan='NONE').count(),
        }
        counts['TOTAL'] = sum(counts.values()) - counts['NONE']  # Exclude NONE from total
        counts['PREMIUM'] = counts['ADVANCE'] + counts['PRO']  # Premium plans
        return counts
    
    def get_reward_progress(self):
        """Calculate progress towards each reward"""
        
        referral_counts = self.get_referral_counts_by_plan()
        total_referrals = referral_counts['TOTAL']
        advance_referrals = referral_counts['ADVANCE'] 
        pro_referrals = referral_counts['PRO']
        
        rewards = self.__class__.objects.none()
        try:
            # Import here to avoid circular import
            from django.apps import apps
            TeamReward = apps.get_model('accounts', 'TeamReward') 
            rewards = TeamReward.objects.filter(is_active=True).order_by('order', 'referrals_required')
        except Exception:
            pass
        progress_data = []
        
        for reward in rewards:
            # Check if basic referral requirement is met
            referrals_met = total_referrals >= reward.referrals_required
            
            # Check additional conditions
            advance_met = advance_referrals >= reward.advance_referrals_required
            pro_met = pro_referrals >= reward.pro_referrals_required
            
            # Overall eligibility
            is_eligible = referrals_met and advance_met and pro_met
            
            # Check if already achieved
            is_achieved = hasattr(self, 'user') and self.user.reward_achievements.filter(reward=reward).exists()
            
            progress_data.append({
                'reward': reward,
                'total_referrals_progress': min(100, (total_referrals / reward.referrals_required) * 100) if reward.referrals_required > 0 else 100,
                'advance_progress': min(100, (advance_referrals / reward.advance_referrals_required) * 100) if reward.advance_referrals_required > 0 else 100,
                'pro_progress': min(100, (pro_referrals / reward.pro_referrals_required) * 100) if reward.pro_referrals_required > 0 else 100,
                'is_eligible': is_eligible,
                'is_achieved': is_achieved,
                'referrals_needed': max(0, reward.referrals_required - total_referrals),
                'advance_needed': max(0, reward.advance_referrals_required - advance_referrals),
                'pro_needed': max(0, reward.pro_referrals_required - pro_referrals),
            })
        
        return progress_data
    
    def save(self, *args, **kwargs):
        """
        Override save to trigger commission calculation when plan is upgraded
        or when referral chain changes
        """
        # Check if this is an update (not a new instance)
        if self.pk:
            try:
                old_instance = UserProfile.objects.get(pk=self.pk)
                old_plan = old_instance.plan
                old_referred_by = old_instance.referred_by
                
                # Save first to ensure the changes are persisted
                super().save(*args, **kwargs)
                
                # Handle plan upgrade from NONE to paid plan
                if old_plan == 'NONE' and self.plan != 'NONE':
                    from .referrals import calculate_commissions_for_plan_upgrade
                    calculate_commissions_for_plan_upgrade(self.user, self.plan)
                
                # Handle referral chain changes
                elif old_referred_by != self.referred_by:
                    from .referrals import handle_referral_chain_change
                    handle_referral_chain_change(self.user, old_referred_by, self.referred_by, self.plan)
                
                return
                
            except UserProfile.DoesNotExist:
                pass
        
        # Normal save for new instances
        super().save(*args, **kwargs)

# For quick multi-level lookup of referral chain
class Referral(models.Model):
    referred = models.OneToOneField(User, on_delete=models.CASCADE, related_name='referral_info')
    level_1 = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='level1_referrals')
    level_2 = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='level2_referrals')
    level_3 = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='level3_referrals')

    def __str__(self):
        return f"{self.referred.username} - Referral Levels"

# Commission Rate Configuration - Plan-wise commission rates
class CommissionRate(models.Model):
    seller_plan = models.CharField(max_length=20, choices=PLAN_CHOICES)  # Plan of person selling
    sold_plan = models.ForeignKey(Plan, on_delete=models.CASCADE)  # Plan being sold
    level_1_percentage = models.DecimalField(max_digits=5, decimal_places=2)  # Level 1 commission %
    level_2_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=8.00)  # Level 2 commission %
    level_3_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=2.00)  # Level 3 commission %
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['seller_plan', 'sold_plan']

    def __str__(self):
        return f"{self.seller_plan} selling {self.sold_plan.name} - L1: {self.level_1_percentage}%"

# Commission entries
class Commission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # earning user
    referred_user = models.ForeignKey(User, related_name='referred_commissions', on_delete=models.CASCADE)
    sold_plan = models.ForeignKey(Plan, null=True, blank=True, on_delete=models.CASCADE)  # Plan that was sold
    seller_plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='NONE')  # Plan of the seller
    level = models.IntegerField()
    percentage_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)  # Percentage used
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment = models.ForeignKey('Payment', null=True, blank=True, on_delete=models.CASCADE)  # Link to payment
    created_at = models.DateTimeField(auto_now_add=True)
    admin_note = models.TextField(blank=True, null=True, help_text="Admin notes about commission changes")  # Track referral changes
    is_active = models.BooleanField(default=True, help_text="False if referral chain changed")  # Track if still valid

    def __str__(self):
        return f"Commission for {self.user.username} - Level {self.level} - Rs.{self.amount}"

# Team reward configuration (editable by admin)
class TeamReward(models.Model):
    referrals_required = models.PositiveIntegerField()
    reward_name = models.CharField(max_length=255)
    reward_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    advance_referrals_required = models.PositiveIntegerField(default=0, help_text="Minimum Advance plan referrals required")
    pro_referrals_required = models.PositiveIntegerField(default=0, help_text="Minimum Pro plan referrals required")
    condition_text = models.TextField(blank=True, null=True, help_text="Display text for conditions")
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    
    class Meta:
        ordering = ['order', 'referrals_required']

    def __str__(self):
        return f"{self.reward_name} ({self.referrals_required} referrals)"
    
    def has_conditions(self):
        """Check if this reward has additional conditions beyond total referrals"""
        return self.advance_referrals_required > 0 or self.pro_referrals_required > 0

# User reward achievements
class UserRewardAchievement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reward_achievements')
    reward = models.ForeignKey(TeamReward, on_delete=models.CASCADE)
    achieved_at = models.DateTimeField(auto_now_add=True)
    is_claimed = models.BooleanField(default=False)
    admin_notes = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ['user', 'reward']
    
    def __str__(self):
        return f"{self.user.username} - {self.reward.reward_name}"

# Manual payment model
class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, null=True, blank=True, on_delete=models.SET_NULL)
    course = models.ForeignKey(Course, null=True, blank=True, on_delete=models.SET_NULL)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    proof = models.FileField(upload_to='payment_proofs/', blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount} ({self.status})"


# Signals are now handled in accounts/signals.py to avoid conflicts



### Directory: accounts/models.py
from django.db import models
from django.contrib.auth.models import User

class Plan(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

class UserPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    purchase_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.plan.name}"
    
# Plans
PLAN_CHOICES = [
    ('BASIC', 'Basic'),
    ('STANDARD', 'Standard'),
    ('ADVANCE', 'Advance'),
    ('PRO', 'Pro'),
]

PLAN_PRICES = {
    'BASIC': 3000,
    'STANDARD': 7000,
    'ADVANCE': 13000,
    'PRO': 20000,
}

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES)
    referred_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='referrals')

    def __str__(self):
        return self.user.username

    def total_direct_referrals(self):
        return self.user.referrals.count()


class Referral(models.Model):
    referred = models.OneToOneField(User, on_delete=models.CASCADE, related_name='referral_info')
    level_1 = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='level1_referrals')
    level_2 = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='level2_referrals')
    level_3 = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='level3_referrals')

    def __str__(self):
        return f"{self.referred.username} - Referral Levels"


class Commission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # earning user
    referred_user = models.ForeignKey(User, related_name='referred_commissions', on_delete=models.CASCADE)
    level = models.IntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Commission for {self.user.username} - ₹{self.amount}"


class TeamReward(models.Model):
    referrals_required = models.PositiveIntegerField()
    reward_name = models.CharField(max_length=255)
    condition = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.referrals_required} – {self.reward_name}"
    
   
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django import forms
from .models import Plan, UserPlan, UserProfile, Referral, Commission, TeamReward, UserRewardAchievement, Payment, Course, SiteSetting, CommissionRate
from .referrals import handle_successful_payment, handle_successful_referral

admin.site.site_header = "AFAA Admin Panel"
admin.site.site_title = "Afaa Elevate Admin"
admin.site.index_title = "Welcome to Afaa Elevate Administration"

# Enhanced User Admin
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'date_joined', 'get_plan', 'get_referrals')
    list_filter = ('is_active', 'is_staff', 'date_joined', 'userprofile__plan')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    actions = ['activate_users', 'deactivate_users']
    
    def get_plan(self, obj):
        try:
            return obj.userprofile.plan
        except:
            return "No Profile"
    get_plan.short_description = "Plan"
    
    def get_referrals(self, obj):
        try:
            return obj.userprofile.total_direct_referrals()
        except:
            return 0
    get_referrals.short_description = "Referrals"
    
    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} users activated ✅")
    activate_users.short_description = "Activate selected users"
    
    def deactivate_users(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} users deactivated ❌")
    deactivate_users.short_description = "Deactivate selected users"

# Register SiteSetting to be editable in admin
@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'phone', 'email', 'facebook', 'instagram', 'linkedin', 'youtube', 'whatsapp', 'whatsapp_channel')
    
    def has_add_permission(self, request):
        # Allow adding if no settings exist yet
        return not SiteSetting.objects.exists()

# Unregister the default User admin and register custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_price_display', 'course_count', 'user_count', 'description')
    search_fields = ('name', 'description')
    ordering = ('price',)
    
    def get_price_display(self, obj):
        return f"Rs {obj.price}"
    get_price_display.short_description = "Price"
    
    def course_count(self, obj):
        count = obj.course_set.count()
        return f"📚 {count} course{'s' if count != 1 else ''}"
    course_count.short_description = "Courses"
    
    def user_count(self, obj):
        from .models import UserProfile
        count = UserProfile.objects.filter(plan=obj.name).count()
        return f"👥 {count} user{'s' if count != 1 else ''}"
    user_count.short_description = "Active Users"

class CourseAdminForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = '__all__'
        widgets = {
            'course_link': forms.URLInput(attrs={
                'placeholder': 'https://example.com/course-link',
                'style': 'width: 100%; font-size: 14px; padding: 8px;'
            }),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'style': 'width: 100%; font-size: 14px;'
            }),
            'title': forms.TextInput(attrs={
                'style': 'width: 100%; font-size: 14px; padding: 8px;'
            })
        }

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    form = CourseAdminForm
    list_display = ('title', 'get_plan_display', 'get_course_link_display', 'created_at')
    search_fields = ('title', 'plan__name', 'description', 'course_link')
    list_filter = ('plan', 'created_at')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Course Information', {
            'fields': ('title', 'description', 'plan'),
            'description': 'Basic course details and plan assignment'
        }),
        ('Course Access', {
            'fields': ('course_link',),
            'description': '🔗 Add the direct link where students can access this course'
        }),
        ('Media', {
            'fields': ('thumbnail',),
            'description': '📸 Upload course thumbnail image'
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def get_plan_display(self, obj):
        if obj.plan:
            return f"� {obj.plan.name}"
        return "❌ No Plan Assigned"
    get_plan_display.short_description = "Plan"
    
    def get_plan_price(self, obj):
        if obj.plan:
            return f"Rs {obj.plan.price}"
        return "—"
    get_plan_price.short_description = "Plan Price"
    
    def get_course_link_display(self, obj):
        if obj.course_link:
            return f"🔗 {obj.course_link[:50]}{'...' if len(obj.course_link) > 50 else ''}"
        return "❌ No Link"
    get_course_link_display.short_description = "Course Link"

    def has_thumbnail(self, obj):
        return "✅ Yes" if obj.thumbnail else "❌ No"
    has_thumbnail.short_description = "Thumbnail"

@admin.register(UserPlan)
class UserPlanAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'plan_price', 'purchase_date', 'days_since_purchase')
    search_fields = ('user__username', 'plan__name')
    list_filter = ('plan', 'purchase_date')
    readonly_fields = ('purchase_date', 'days_since_purchase')
    actions = ['create_commission_for_plans']
    
    def plan_price(self, obj):
        return f"Rs. {obj.plan.price}"
    plan_price.short_description = "Price"
    
    def days_since_purchase(self, obj):
        from django.utils import timezone
        diff = timezone.now() - obj.purchase_date
        return f"{diff.days} days"
    days_since_purchase.short_description = "Days Ago"
    
    def create_commission_for_plans(self, request, queryset):
        created = 0
        for user_plan in queryset:
            try:
                handle_successful_referral(user_plan.user)
                created += 1
            except Exception:
                pass
        self.message_user(request, f"Commission created for {created} plans ✅")
    create_commission_for_plans.short_description = "Create commissions for selected plans"

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'mobile', 'dob', 'referral_code', 'referred_by', 'total_referrals')
    search_fields = ('user__username', 'referred_by__username', 'mobile', 'referral_code')
    list_filter = ('plan', 'dob', 'referred_by')
    readonly_fields = ('referral_code', 'total_referrals')
    actions = ['set_to_none', 'upgrade_to_basic', 'upgrade_to_standard', 'upgrade_to_advance', 'upgrade_to_pro']
    
    def save_model(self, request, obj, form, change):
        """Custom save to ensure commission calculation and show admin message"""
        if change:  # Only for updates, not new objects
            try:
                # Get original object to compare
                original = UserProfile.objects.get(pk=obj.pk)
                old_plan = original.plan
                new_plan = obj.plan
                
                # Save the object (this will trigger our custom save method)
                super().save_model(request, obj, form, change)
                
                # Show message if commission was triggered
                if old_plan == 'NONE' and new_plan != 'NONE':
                    self.message_user(
                        request, 
                        f"✅ Plan upgraded for {obj.user.username}: {old_plan} → {new_plan}. Commissions calculated automatically!",
                        messages.SUCCESS
                    )
                elif old_plan != new_plan:
                    self.message_user(
                        request,
                        f"ℹ️ Plan changed for {obj.user.username}: {old_plan} → {new_plan}",
                        messages.INFO
                    )
                
                # Show message if referral chain changed
                if original.referred_by != obj.referred_by:
                    old_referrer = original.referred_by.username if original.referred_by else "None"
                    new_referrer = obj.referred_by.username if obj.referred_by else "None"
                    self.message_user(
                        request,
                        f"🔄 Referral chain changed for {obj.user.username}: {old_referrer} → {new_referrer}. Commission history updated!",
                        messages.WARNING
                    )
            except UserProfile.DoesNotExist:
                # New object
                super().save_model(request, obj, form, change)
        else:
            # New object
            super().save_model(request, obj, form, change)
    
    def total_referrals(self, obj):
        return obj.total_direct_referrals()
    total_referrals.short_description = "Direct Referrals"
    
    def set_to_none(self, request, queryset):
        updated = 0
        for profile in queryset:
            profile.plan = 'NONE'
            profile.save()  # This will trigger commission calculation if needed
            updated += 1
        self.message_user(request, f"{updated} users plan removed (set to NONE) 🚫")
    set_to_none.short_description = "Remove plan (set to NONE)"
    
    def upgrade_to_basic(self, request, queryset):
        updated = 0
        commissions_created = 0
        for profile in queryset:
            old_plan = profile.plan
            profile.plan = 'BASIC'
            profile.save()  # This will trigger commission calculation if NONE → BASIC
            updated += 1
            if old_plan == 'NONE':
                commissions_created += 1
        self.message_user(request, f"{updated} users upgraded to BASIC plan ✅ ({commissions_created} commission triggers)")
    upgrade_to_basic.short_description = "Upgrade to BASIC plan"
    
    def upgrade_to_standard(self, request, queryset):
        updated = 0
        commissions_created = 0
        for profile in queryset:
            old_plan = profile.plan
            profile.plan = 'STANDARD'
            profile.save()  # This will trigger commission calculation if NONE → STANDARD
            updated += 1
            if old_plan == 'NONE':
                commissions_created += 1
        self.message_user(request, f"{updated} users upgraded to STANDARD plan ✅ ({commissions_created} commission triggers)")
    upgrade_to_standard.short_description = "Upgrade to STANDARD plan"
    
    def upgrade_to_advance(self, request, queryset):
        updated = 0
        commissions_created = 0
        for profile in queryset:
            old_plan = profile.plan
            profile.plan = 'ADVANCE'
            profile.save()  # This will trigger commission calculation if NONE → ADVANCE
            updated += 1
            if old_plan == 'NONE':
                commissions_created += 1
        self.message_user(request, f"{updated} users upgraded to ADVANCE plan ✅ ({commissions_created} commission triggers)")
    upgrade_to_advance.short_description = "Upgrade to ADVANCE plan"
    
    def upgrade_to_pro(self, request, queryset):
        updated = 0
        commissions_created = 0
        for profile in queryset:
            old_plan = profile.plan
            profile.plan = 'PRO'
            profile.save()  # This will trigger commission calculation if NONE → PRO
            updated += 1
            if old_plan == 'NONE':
                commissions_created += 1
        self.message_user(request, f"{updated} users upgraded to PRO plan ✅ ({commissions_created} commission triggers)")
    upgrade_to_pro.short_description = "Upgrade to PRO plan"

@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ('referred', 'level_1', 'level_2', 'level_3')
    search_fields = ('referred__username',)

@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'referred_user', 'sold_plan', 'level', 'amount', 'percentage_rate', 'is_active_status', 'created_at')
    search_fields = ('user__username', 'referred_user__username', 'admin_note')
    list_filter = ('level', 'is_active', 'created_at', 'sold_plan')
    readonly_fields = ('created_at',)
    fields = ('user', 'referred_user', 'sold_plan', 'level', 'percentage_rate', 'amount', 'is_active', 'admin_note', 'created_at')
    ordering = ('-created_at',)
    
    def is_active_status(self, obj):
        return "✅ Active" if obj.is_active else "❌ Inactive"
    is_active_status.short_description = "Status"

@admin.register(TeamReward)
class TeamRewardAdmin(admin.ModelAdmin):
    list_display = ('reward_name', 'referrals_required', 'advance_referrals_required', 'pro_referrals_required', 'reward_amount', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    search_fields = ('reward_name', 'condition_text')
    list_filter = ('is_active', 'referrals_required')
    ordering = ('order', 'referrals_required')
    
    fieldsets = (
        ('Reward Details', {
            'fields': ('reward_name', 'reward_amount', 'order', 'is_active')
        }),
        ('Requirements', {
            'fields': ('referrals_required', 'advance_referrals_required', 'pro_referrals_required')
        }),
        ('Conditions', {
            'fields': ('condition_text',)
        })
    )

@admin.register(UserRewardAchievement)
class UserRewardAchievementAdmin(admin.ModelAdmin):
    list_display = ('user', 'reward_name', 'achieved_at', 'is_claimed')
    list_filter = ('is_claimed', 'achieved_at', 'reward__reward_name')
    search_fields = ('user__username', 'reward__reward_name')
    readonly_fields = ('user', 'reward', 'achieved_at')
    ordering = ('-achieved_at',)
    list_per_page = 50
    actions = ['mark_as_claimed', 'mark_as_unclaimed']
    
    def reward_name(self, obj):
        return obj.reward.reward_name
    reward_name.short_description = "Reward"
    
    def mark_as_claimed(self, request, queryset):
        updated = queryset.update(is_claimed=True)
        self.message_user(request, f"{updated} achievements marked as claimed ✅")
    mark_as_claimed.short_description = "Mark as claimed"
    
    def mark_as_unclaimed(self, request, queryset):
        updated = queryset.update(is_claimed=False)
        self.message_user(request, f"{updated} achievements marked as unclaimed ⏳")
    mark_as_unclaimed.short_description = "Mark as unclaimed"

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'plan__name')
    readonly_fields = ('user', 'plan', 'amount', 'proof', 'created_at')
    ordering = ('-created_at',)
    list_per_page = 20
    actions = ['approve_payments', 'reject_payments']

    def approve_payments(self, request, queryset):
        updated = 0
        for payment in queryset:
            if payment.status != 'approved':
                payment.status = 'approved'
                payment.save()

                # Create UserPlan to grant course access
                UserPlan.objects.get_or_create(user=payment.user, plan=payment.plan)

                # Update profile plan text
                try:
                    profile = payment.user.userprofile
                    profile.plan = payment.plan.name.upper()
                    profile.save()
                except Exception:
                    pass

                # award referrals/commissions using new system
                try:
                    handle_successful_payment(payment)
                except Exception as e:
                    messages.warning(request, f"Commission calculation error for {payment.user.username}: {str(e)}")
                    pass

                updated += 1

        self.message_user(request, f"{updated} payment(s) approved ✅", level=messages.SUCCESS)
    approve_payments.short_description = "Approve selected payments"

    def reject_payments(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f"{updated} payment(s) rejected ❌", level=messages.ERROR)
    reject_payments.short_description = "Reject selected payments"

@admin.register(CommissionRate)
class CommissionRateAdmin(admin.ModelAdmin):
    list_display = ('seller_plan', 'sold_plan', 'level_1_percentage', 'level_2_percentage', 'level_3_percentage', 'is_active')
    list_filter = ('seller_plan', 'sold_plan', 'is_active')
    search_fields = ('seller_plan', 'sold_plan__name')
    list_editable = ('level_1_percentage', 'level_2_percentage', 'level_3_percentage', 'is_active')
    ordering = ('seller_plan', 'sold_plan')
    actions = ['activate_rates', 'deactivate_rates']
    
    def activate_rates(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} commission rate(s) activated ✅")
    activate_rates.short_description = "Activate selected commission rates"
    
    def deactivate_rates(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} commission rate(s) deactivated ❌")
    deactivate_rates.short_description = "Deactivate selected commission rates"

# Enhanced Commission Admin
class CommissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'referred_user', 'sold_plan', 'seller_plan', 'level', 'percentage_rate', 'amount', 'created_at')
    list_filter = ('level', 'sold_plan', 'seller_plan', 'created_at')
    search_fields = ('user__username', 'referred_user__username', 'sold_plan__name')
    readonly_fields = ('user', 'referred_user', 'sold_plan', 'seller_plan', 'level', 'percentage_rate', 'amount', 'payment', 'created_at')
    ordering = ('-created_at',)
    list_per_page = 25
    
    def has_add_permission(self, request):
        return False  # Commissions are auto-generated
    
    def has_change_permission(self, request, obj=None):
        return False  # Read-only for data integrity

# Re-register Commission with enhanced admin
admin.site.unregister(Commission)
admin.site.register(Commission, CommissionAdmin)

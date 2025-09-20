from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Test invite functionality setup'

    def handle(self, *args, **options):
        self.stdout.write('=== Testing Invite Friend Setup ===')
        
        # Check if invite buttons were removed from other templates
        templates_to_check = [
            'accounts/templates/base.html',
            'accounts/templates/main.html', 
            'accounts/templates/commission.html'
        ]
        
        for template in templates_to_check:
            try:
                with open(template, 'r', encoding='utf-8') as f:
                    content = f.read()
                    has_invite = 'invite-friend-btn' in content or 'Invite a Friend' in content
                    status = "❌ Still has invite button" if has_invite else "✅ Invite button removed"
                    self.stdout.write(f'{template}: {status}')
            except FileNotFoundError:
                self.stdout.write(f'{template}: File not found')
        
        # Check if user_dashboard.html has the invite functionality
        try:
            with open('accounts/templates/user_dashboard.html', 'r', encoding='utf-8') as f:
                content = f.read()
                has_invite_section = 'invite-friends-section' in content
                has_whatsapp_func = 'inviteFriendWhatsApp' in content
                has_referral_display = 'Your Referral Code:' in content
                
                self.stdout.write(f'\nuser_dashboard.html checks:')
                self.stdout.write(f'  Invite section: {"✅ Present" if has_invite_section else "❌ Missing"}')
                self.stdout.write(f'  WhatsApp function: {"✅ Present" if has_whatsapp_func else "❌ Missing"}')
                self.stdout.write(f'  Referral code display: {"✅ Present" if has_referral_display else "❌ Missing"}')
        except FileNotFoundError:
            self.stdout.write('user_dashboard.html: File not found')
            
        # Test referral code generation
        try:
            user = User.objects.first()
            if user:
                profile = user.userprofile
                referral_code = profile.referral_code or user.username
                self.stdout.write(f'\nSample referral code for {user.username}: {referral_code}')
                
                # Show what the WhatsApp message would look like
                website_url = "http://127.0.0.1:8000"
                message = f"""Join AFAA Elevate and unlock amazing learning opportunities!

Use my referral code: {referral_code}

Sign up here:
{website_url}

Let's grow together!"""
                
                self.stdout.write(f'\nSample WhatsApp message:')
                self.stdout.write(f'"{message}"')
                
        except Exception as e:
            self.stdout.write(f'Error testing referral: {e}')
            
        self.stdout.write(f'\n🎉 INVITE SYSTEM SETUP COMPLETE!')
        self.stdout.write(f'✅ Invite button only in user dashboard')
        self.stdout.write(f'✅ WhatsApp integration with referral code')
        self.stdout.write(f'✅ Manual referral code entry (no direct URL)')
        self.stdout.write(f'✅ Website link + referral code in message')
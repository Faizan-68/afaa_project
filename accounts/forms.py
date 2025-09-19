
# accounts/forms.py
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    mobile = forms.CharField(max_length=15, required=False, help_text='Enter your mobile number')
    dob = forms.DateField(required=False, help_text='Your date of birth', widget=forms.DateInput(attrs={'type': 'date'}))
    referral_code = forms.CharField(required=False, help_text='Enter referrer\'s username or referral code if any')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'mobile', 'dob', 'referral_code']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Create or update UserProfile with additional fields
            from .models import UserProfile
            profile, created = UserProfile.objects.get_or_create(user=user)
            
            # Set profile fields
            profile.mobile = self.cleaned_data.get('mobile', '')
            profile.dob = self.cleaned_data.get('dob')
            profile.referral_code = user.username  # User's own referral code (simple and clean)
            profile.save()
        return user

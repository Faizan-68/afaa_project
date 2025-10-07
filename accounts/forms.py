
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

    def clean_email(self):
        """Check if email is already registered"""
        email = self.cleaned_data.get('email')
        if email:
            # Check if email already exists (case-insensitive)
            if User.objects.filter(email__iexact=email).exists():
                raise forms.ValidationError("This email is already registered. Please use a different email or try to login.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # The UserProfile is created by signals, so just update it with form data
            from .models import UserProfile
            profile = user.userprofile  # Should exist due to signal
            
            # Set profile fields from form
            profile.mobile = self.cleaned_data.get('mobile', '')
            profile.dob = self.cleaned_data.get('dob')
            # referral_code is already set by signal to username, no need to override
            profile.save()
        return user

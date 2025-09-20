#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'afaa_project.settings')
django.setup()

from accounts.forms import SignUpForm

# Test data with referral code
test_data_with_referral = {
    'username': 'testuser1',
    'email': 'test1@example.com',
    'password1': 'testpass123',
    'password2': 'testpass123',
    'mobile': '03001234567',
    'dob': '1990-01-01',
    'referral_code': 'faizan'  # existing user
}

# Test data without referral code  
test_data_without_referral = {
    'username': 'testuser2',
    'email': 'test2@example.com',
    'password1': 'testpass123',
    'password2': 'testpass123',
    'mobile': '03007654321',
    'dob': '1995-05-05',
    'referral_code': ''  # no referral
}

print("Testing SignUp Form...")
print("=" * 50)

# Test 1: With referral code
print("TEST 1: With referral code")
print("-" * 30)
form1 = SignUpForm(test_data_with_referral)
if form1.is_valid():
    print("Form is valid")
    user1 = form1.save()
    print(f"User created: {user1.username}")
else:
    print("Form errors:", form1.errors)

print("\n" + "="*50)

# Test 2: Without referral code
print("TEST 2: Without referral code")  
print("-" * 30)
form2 = SignUpForm(test_data_without_referral)
if form2.is_valid():
    print("Form is valid")
    user2 = form2.save()
    print(f"User created: {user2.username}")
else:
    print("Form errors:", form2.errors)

print("\nDone!")
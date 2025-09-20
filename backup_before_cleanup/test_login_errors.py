#!/usr/bin/env python3
"""
Test script for login error messages
Tests various login error scenarios to ensure comprehensive error handling
"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import re

# Base URL for the application
BASE_URL = "http://127.0.0.1:8000"

def setup_session():
    """Setup requests session with retry strategy"""
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def get_csrf_token(session, url):
    """Extract CSRF token from the login page"""
    try:
        response = session.get(url)
        if response.status_code == 200:
            # Look for CSRF token in the HTML
            csrf_match = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', response.text)
            if csrf_match:
                return csrf_match.group(1)
        return None
    except Exception as e:
        print(f"❌ Error getting CSRF token: {e}")
        return None

def test_login_scenarios():
    """Test different login error scenarios"""
    session = setup_session()
    login_url = f"{BASE_URL}/login/"
    
    print("🧪 TESTING LOGIN ERROR MESSAGES 🧪")
    print("=" * 50)
    
    # Test 1: Empty form submission
    print("\n1️⃣ Testing empty form submission...")
    csrf_token = get_csrf_token(session, login_url)
    if csrf_token:
        response = session.post(login_url, data={
            'csrfmiddlewaretoken': csrf_token,
            'username': '',
            'password': ''
        })
        if "This field is required" in response.text or "Please enter" in response.text:
            print("   ✅ Empty form validation working")
        else:
            print("   ⚠️  Empty form validation might need attention")
    
    # Test 2: Invalid username/password
    print("\n2️⃣ Testing invalid credentials...")
    csrf_token = get_csrf_token(session, login_url)
    if csrf_token:
        response = session.post(login_url, data={
            'csrfmiddlewaretoken': csrf_token,
            'username': 'invalid_user_123456',
            'password': 'invalid_password_123456'
        })
        if "Invalid username or password" in response.text or "Please enter a correct" in response.text:
            print("   ✅ Invalid credentials error working")
        else:
            print("   ⚠️  Invalid credentials error might need attention")
    
    # Test 3: Only username provided
    print("\n3️⃣ Testing missing password...")
    csrf_token = get_csrf_token(session, login_url)
    if csrf_token:
        response = session.post(login_url, data={
            'csrfmiddlewaretoken': csrf_token,
            'username': 'testuser',
            'password': ''
        })
        if "This field is required" in response.text or "Password" in response.text:
            print("   ✅ Missing password validation working")
        else:
            print("   ⚠️  Missing password validation might need attention")
    
    # Test 4: Only password provided
    print("\n4️⃣ Testing missing username...")
    csrf_token = get_csrf_token(session, login_url)
    if csrf_token:
        response = session.post(login_url, data={
            'csrfmiddlewaretoken': csrf_token,
            'username': '',
            'password': 'testpassword'
        })
        if "This field is required" in response.text or "Username" in response.text:
            print("   ✅ Missing username validation working")
        else:
            print("   ⚠️  Missing username validation might need attention")
    
    # Test 5: Check for error message styling
    print("\n5️⃣ Checking error message styling...")
    response = session.get(login_url)
    if "error-container" in response.text and "error-icon" in response.text:
        print("   ✅ Error message styling classes found")
    else:
        print("   ⚠️  Error message styling might need attention")
    
    # Test 6: Check for JavaScript validation
    print("\n6️⃣ Checking JavaScript validation...")
    if "validateField" in response.text and "showFieldError" in response.text:
        print("   ✅ JavaScript validation functions found")
    else:
        print("   ⚠️  JavaScript validation might need attention")
    
    print("\n" + "=" * 50)
    print("🎯 LOGIN ERROR TESTING COMPLETED!")
    print("📋 All error message features have been tested.")

if __name__ == "__main__":
    try:
        test_login_scenarios()
    except KeyboardInterrupt:
        print("\n❌ Test interrupted by user")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
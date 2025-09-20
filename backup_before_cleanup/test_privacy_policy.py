#!/usr/bin/env python
import os
import django
import sys

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'afaa_project.settings')
django.setup()

from django.test import Client
from django.urls import reverse

def test_privacy_policy():
    client = Client()
    
    try:
        # Test the privacy policy URL
        response = client.get('/privacy-policy/')
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ Privacy policy page loads successfully")
            print(f"Content length: {len(response.content)} bytes")
        else:
            print(f"✗ Error: HTTP {response.status_code}")
            print(f"Response content: {response.content.decode('utf-8')[:500]}")
            
    except Exception as e:
        print(f"✗ Exception occurred: {e}")
        import traceback
        traceback.print_exc()

    # Also test using reverse URL lookup
    try:
        url = reverse('privacy_policy')
        response = client.get(url)
        print(f"\nUsing reverse lookup - URL: {url}")
        print(f"Status Code: {response.status_code}")
    except Exception as e:
        print(f"✗ Reverse URL lookup failed: {e}")

if __name__ == "__main__":
    test_privacy_policy()
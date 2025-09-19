#!/usr/bin/env python3

import requests

# Test authentication flow
base_url = "http://127.0.0.1:8000"

print("🧪 Testing Authentication Flow...")

# Step 1: Test login page access
print("\n1. Testing login page access...")
response = requests.get(f"{base_url}/login/")
print(f"   Login page status: {response.status_code}")

# Step 2: Test unauthenticated dashboard access (should redirect)
print("\n2. Testing unauthenticated dashboard access...")
response = requests.get(f"{base_url}/dashboard/", allow_redirects=False)
print(f"   Dashboard redirect status: {response.status_code}")
if response.status_code == 302:
    print(f"   Redirect location: {response.headers.get('Location', 'Not found')}")

# Step 3: Test URLs
print("\n3. Testing URL patterns...")
urls_to_test = [
    "/",
    "/login/", 
    "/signup/",
    "/logout/",
    "/courses/",
]

for url in urls_to_test:
    try:
        response = requests.get(f"{base_url}{url}", allow_redirects=False)
        print(f"   {url:<15} -> {response.status_code}")
    except Exception as e:
        print(f"   {url:<15} -> ERROR: {e}")

print("\n✅ Authentication flow test completed!")
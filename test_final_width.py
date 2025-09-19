#!/usr/bin/env python3
"""
Final test for login container width fixes
"""

import requests
import re

BASE_URL = "http://127.0.0.1:8000"

def test_final_width_fix():
    """Test the final width fixes"""
    print("🎯 FINAL WIDTH FIX TESTING 🎯")
    print("=" * 50)
    
    try:
        session = requests.Session()
        response = session.get(f"{BASE_URL}/login/")
        
        if response.status_code == 200:
            content = response.text
            
            print("\n1️⃣ Checking CSS includes...")
            if "login-width-fix.css" in content:
                print("   ✅ Additional width fix CSS included")
            else:
                print("   ⚠️  Additional CSS not found")
                
            print("\n2️⃣ Checking width constraints...")
            if "width: 420px !important" in content:
                print("   ✅ Fixed width constraint found")
            else:
                print("   ⚠️  Fixed width constraint not found")
                
            print("\n3️⃣ Checking overflow controls...")
            if "overflow: hidden !important" in content:
                print("   ✅ Overflow control found")
            else:
                print("   ⚠️  Overflow control not found")
                
            print("\n4️⃣ Checking box-sizing...")
            if "box-sizing: border-box !important" in content:
                print("   ✅ Box sizing constraint found")
            else:
                print("   ⚠️  Box sizing constraint not found")
                
            print("\n5️⃣ Checking mobile responsive...")
            if "calc(100vw - 40px)" in content:
                print("   ✅ Mobile responsive width found")
            else:
                print("   ⚠️  Mobile responsive width not found")
                
            # Test error scenario
            print("\n6️⃣ Testing with error scenario...")
            csrf_match = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', content)
            if csrf_match:
                csrf_token = csrf_match.group(1)
                error_response = session.post(f"{BASE_URL}/login/", data={
                    'csrfmiddlewaretoken': csrf_token,
                    'username': 'test_width_user',
                    'password': 'test_width_pass'
                })
                
                if error_response.status_code == 200:
                    print("   ✅ Error scenario test completed")
                    if "width: 420px !important" in error_response.text:
                        print("   ✅ Width constraint maintained during errors")
                    else:
                        print("   ⚠️  Width constraint lost during errors")
            
        else:
            print(f"   ❌ Failed to load login page: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Test error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 FINAL WIDTH TESTING COMPLETED!")
    print("📌 Refresh browser to see fixed width")

if __name__ == "__main__":
    test_final_width_fix()
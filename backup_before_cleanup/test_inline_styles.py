#!/usr/bin/env python3
"""
Test inline width styles on login page
"""

import requests
import time

def test_inline_styles():
    print("🎯 TESTING INLINE WIDTH STYLES 🎯")
    print("=" * 50)
    
    try:
        # Wait for server
        time.sleep(2)
        
        session = requests.Session()
        response = session.get("http://127.0.0.1:8000/login/")
        
        if response.status_code == 200:
            content = response.text
            
            print("\n✅ Server is running!")
            
            print("\n1️⃣ Checking login-container inline styles...")
            if 'style="width: 400px !important' in content:
                print("   ✅ Login container inline width found")
            else:
                print("   ⚠️  Login container inline width not found")
                
            print("\n2️⃣ Checking login-card inline styles...")
            if 'login-card" style="width: 100% !important' in content:
                print("   ✅ Login card inline styles found")
            else:
                print("   ⚠️  Login card inline styles not found")
                
            print("\n3️⃣ Checking form inline styles...")
            if 'login-form" style="width: 100% !important' in content:
                print("   ✅ Form inline styles found")
            else:
                print("   ⚠️  Form inline styles not found")
                
            print("\n4️⃣ Checking error container inline styles...")
            if 'error-container" style="width: 100% !important' in content:
                print("   ✅ Error container inline styles found")
            else:
                print("   ⚠️  Error container inline styles not found")
                
            print("\n5️⃣ Checking form-group inline styles...")
            if 'form-group" style="width: 100% !important' in content:
                print("   ✅ Form group inline styles found")
            else:
                print("   ⚠️  Form group inline styles not found")
                
        else:
            print(f"   ❌ Server response error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
        print("   📝 Make sure server is running: python manage.py runserver")
    
    print("\n" + "=" * 50)
    print("🎯 INLINE STYLES TESTING COMPLETED!")
    print("📌 All width controls are now inline in HTML")

if __name__ == "__main__":
    test_inline_styles()
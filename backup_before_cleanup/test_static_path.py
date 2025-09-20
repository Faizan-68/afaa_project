import os
from django.conf import settings

# Test static path configuration
print("BASE_DIR:", settings.BASE_DIR)
print("STATIC_URL:", settings.STATIC_URL)
print("STATICFILES_DIRS:", settings.STATICFILES_DIRS)
print("STATIC_ROOT:", settings.STATIC_ROOT)

# Check if payment logos exist
static_dir = settings.STATICFILES_DIRS[0]
payment_logos_dir = os.path.join(static_dir, 'Media', 'payment-logos')

print("\nPayment logos directory:", payment_logos_dir)
print("Directory exists:", os.path.exists(payment_logos_dir))

if os.path.exists(payment_logos_dir):
    print("Files in payment-logos directory:")
    for file in os.listdir(payment_logos_dir):
        print(f"  - {file}")
        
# Test the exact path used in template
test_file = os.path.join(static_dir, 'Media', 'payment-logos', 'easypaisa.png')
print(f"\nTest file path: {test_file}")
print(f"File exists: {os.path.exists(test_file)}")
# accounts/context_processors.py
from .models import SiteSetting

def site_settings(request):
    return {'site_settings': SiteSetting.objects.first()}

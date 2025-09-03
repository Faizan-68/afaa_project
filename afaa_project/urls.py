from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('', include('django.contrib.auth.urls')),
    path('accounts/', include('allauth.urls')), 
    # path('payments/', include('payments.urls')), 
]

# Static and media file serving during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    
#Client ID = 827122979952-1d0v2f1pt0irmbd6p0mr4kbr8si9dqpt.apps.googleusercontent.com
#Client secret = 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
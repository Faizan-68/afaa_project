from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Your app
    path('', include('accounts.urls')),
]


# Static and media file serving during development
if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    
#Client ID = 827122979952-1d0v2f1pt0irmbd6p0mr4kbr8si9dqpt.apps.googleusercontent.com
#Client secret = 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
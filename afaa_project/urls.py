from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.urls import re_path

urlpatterns = [
    path('afaaelevate/', admin.site.urls),

    # Your app
    path('', include('accounts.urls')),
]


# Static and media file serving for both development and production
if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # Force serve media files in production-like mode (for development server)
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]
    # Also serve static files in production mode
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    
#Client ID = 827122979952-1d0v2f1pt0irmbd6p0mr4kbr8si9dqpt.apps.googleusercontent.com
#Client secret = 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
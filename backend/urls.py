# backend/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings # For serving media files
from django.conf.urls.static import static # For serving media files

urlpatterns = [
    path('admin/', admin.site.urls), # Django admin site
    path('api/', include('doc_ai_api.urls')), # Map /api/ to your app's urls.py
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
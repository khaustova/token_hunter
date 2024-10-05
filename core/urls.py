import debug_toolbar
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django_telethon.urls import django_telethon_urls

admin.autodiscover()

urlpatterns = [
    path("", include("token_hunter.urls")),
    path("", admin.site.urls),
    path('telegram/', django_telethon_urls()),
    path("__debug__/", include(debug_toolbar.urls)),
]

if bool(settings.DEBUG):
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
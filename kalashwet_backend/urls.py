"""
URL configuration for kalashwet_backend project.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),

    # Customer storefront and management APIs under v1/
    path('v1/', include('user.urls')),
    path('v1/', include('catalog.urls')),
    path('v1/', include('pricing.urls')),
    path('v1/', include('orders.urls')),
    path('v1/', include('payments.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [path('__debug__/', include('debug_toolbar.urls'))]

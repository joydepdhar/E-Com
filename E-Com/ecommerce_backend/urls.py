from django.contrib import admin
from django.urls import path, include
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
from django.conf.urls.static import static

@api_view(['GET'])
def api_root(request):
    return Response({
        "user_app": "/api/user_app/",
        "store": "/api/store/",
        "admin": "/admin/"
    })

urlpatterns = [
    path('', api_root),  # DRF API root at /
    path('admin/', admin.site.urls),
    path('api/user_app/', include('user_app.urls')),
    path('api/store/', include('store.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

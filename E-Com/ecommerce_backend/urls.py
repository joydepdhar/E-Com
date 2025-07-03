from django.contrib import admin
from django.urls import path, include
from rest_framework.decorators import api_view
from rest_framework.response import Response

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

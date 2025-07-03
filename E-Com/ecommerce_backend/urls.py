from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({
        "status": "ok",
        "message": "Django backend is live ✅",
        "api_routes": ["/api/user_app/", "/api/store/"]
    })

urlpatterns = [
    path('', health_check),  # Root URL now responds with JSON
    path('admin/', admin.site.urls),
    path('api/user_app/', include('user_app.urls')),
    path('api/store/', include('store.urls')),
]

from django.urls import include, path


app_name = 'api_v1'

urlpatterns = [
    path('', include('user_app.urls')),
    path('', include('store.urls')),
]

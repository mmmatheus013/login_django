from django.contrib import admin
from django.urls import path, include




urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('accounts.urls')),
    path('api/v1/', include('authentication.urls')),
    path('auth/', include('allauth.urls')),
    path('api/v1/', include('plans.urls')),
   
]

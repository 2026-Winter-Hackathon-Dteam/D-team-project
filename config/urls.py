from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('spaces/', include('spaces.urls')),
    path('teams/', include('teams.urls')),
    path('analysis/', include('analysis.urls')),
]

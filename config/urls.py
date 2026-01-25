from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('', include('spaces.urls')),
    path('', include('teams.urls')),
    path('', include('analysis.urls')),
]

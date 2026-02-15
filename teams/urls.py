from django.urls import path
from . import views

app_name = "teams"

urlpatterns = [
    path("", views.team_index, name="team_index"),
    path('set_current/<uuid:team_id>/', views.set_current_team, name='set_current_team'),
]
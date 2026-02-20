from django.urls import path
from . import views

app_name = "teams"

urlpatterns = [
    path("", views.team_index, name="team_index"),
]
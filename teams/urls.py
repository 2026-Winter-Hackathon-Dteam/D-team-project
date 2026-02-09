from django.urls import path
from . import views

urlpatterns = [
    path("", views.team_index, name="team_index"),
]
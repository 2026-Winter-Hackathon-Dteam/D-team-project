from django.urls import path
from . import views

app_name = "teams"

urlpatterns = [
    path("", views.team_index, name="team_index"),
    path("set-current-team/<uuid:team_id>/", views.set_current_team, name="set_current_team"),
    path("create/", views.create_team, name="create_team"),
    path("delete/", views.delete_team, name="delete_team"),
    path("edit/", views.edit_team, name="edit_team"),
    path("add-member/", views.add_member, name="add_member"),
    path("user-search/", views.user_search, name="user_search"),
    path("delete-member/", views.delete_member, name="delete_member"),
    path("set-leader/", views.set_leader, name="set_leader"),
]
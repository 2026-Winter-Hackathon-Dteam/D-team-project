# teams/views.py

from django.shortcuts import render, get_object_or_404
from .models import Teams, Team_Users
from django.contrib.auth import get_user_model

User = get_user_model()

def team_index(request):
    # チームを作られた順に並べて取り出す
    teams = Teams.objects.all().order_by("created_at")

    # ユーザーがクリックしたチームのIDを取り出す
    # GETパラメータからteam_idを取得（なければNone）
    selected_team_id = request.GET.get("team_id")

    # 選択されたチームの初期値
    selected_team = None
    team_members = []

    # 選択されたチームのIDが取得されているならチームメンバー情報を取り出す
    if selected_team_id:
        selected_team = get_object_or_404(Teams, id=selected_team_id)
        team_members = Team_Users.objects.filter(team=selected_team).select_related("user")

    context = {
        "teams": teams,
        "selected_team": selected_team,
        "team_members": team_members,
    }
    return render(request, "teams/teams.html", context)
# teams/views.py

from django.shortcuts import render, get_object_or_404
from .models import Teams, Team_Users
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required # 追記
from django.views.decorators.http import require_http_methods # 追記

User = get_user_model()
#@login_required #ログイン機能実装後にコメントアウトを外す # 追記
@require_http_methods(["GET"]) # 追記

def team_index(request):
    # チームを作られた順に並べて取り出す
    teams = Teams.objects.all().order_by("created_at")

    # ユーザーがクリックしたチームのIDを取り出す
    # GETパラメータからteam_idを取得（なければNone）
    selected_team_id = request.GET.get("team_id")

       # ここから追記(team_id未指定時)
    if selected_team_id == None:
        selected_team = None
        team_members = []
    
        context = {
            "teams": teams,
            "selected_team": selected_team,
            "team_members": team_members
        }
        return render(request, "teams/teams.html", context)
        
    # ログインユーザー取得（未ログイン時はログイン画面に遷移、space所属確認の時に必要。）
    if getattr(request, "user", None) and request.user.is_authenticated:
        current_user = request.user
    else:
        current_user = get_object_or_404(User, pk="11111111-1111-1111-1111-222222222001") #テスト用ユーザー
        # return redirect('login') #本番用


    # 選択されたチームの初期値
    selected_team = None
    team_members = []

    # 選択されたチームのIDが取得されているならチームメンバー情報を取り出す
    if selected_team_id:
        selected_team = get_object_or_404(
            Teams, 
            id=selected_team_id,
            space_id=current_user.space_id # 追記(5,同一space所属で見れるという権限チェックを追加する)
            )
        team_members = Team_Users.objects.filter(team=selected_team).select_related("user")

    context = {
        "teams": teams,
        "selected_team": selected_team,
        "team_members": team_members,
    }
    return render(request, "teams/teams.html", context)


#コンテキストプロセッサで現在のチームを取得しているため、ここではセッションに保存するだけ（今後残すか検討）
@login_required
def set_current_team(request, team_id):
    """現在のチームをセッションに保存"""
    # ログインユーザー取得（未ログイン時はテスト用ユーザー）
    if getattr(request, "user", None) and request.user.is_authenticated:
        current_user = request.user
    else:
        current_user = get_object_or_404(User, pk="11111111-1111-1111-1111-222222222001")  # テスト用ユーザー
    
    # ユーザーが所属しているか確認
    if Team_Users.objects.filter(user=current_user, team_id=team_id).exists():
        request.session['current_team_id'] = str(team_id)
    # 元のページにリダイレクト
    return redirect(request.META.get('HTTP_REFERER', '/'))
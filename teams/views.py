# teams/views.py

import json
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from .models import Teams, Team_Users
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required # 追記
from django.views.decorators.http import require_http_methods # 追記
from django.views.decorators.http import require_POST
from django.shortcuts import redirect
from django.db.models import Q

User = get_user_model()

@require_http_methods(["GET"])
def set_current_team(request, team_id):
    return redirect(f"{reverse('teams:team_index')}?team_id={team_id}")


#@login_required # ログイン機能実装後に有効化
@require_http_methods(["GET"]) # 追記
def team_index(request):
    # チームを作られた順に並べて取り出す
    teams = Teams.objects.all().order_by("created_at")

    # ユーザーがクリックしたチームのIDを取り出す
    # GETパラメータからteam_idを取得（なければNone）
    selected_team_id = request.GET.get("team_id")

       # ここから追記(team_id未指定時)
    if not selected_team_id:
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


# @login_required  # ログイン機能実装後に有効化
@require_POST
def create_team(request):
    # ===== 開発用 強制ユーザー取得 =====
    if getattr(request, "user", None) and request.user.is_authenticated:
        current_user = request.user
    else:
        current_user = get_object_or_404(
            User,
            pk="11111111-1111-1111-1111-222222222001"  # テスト用管理者
        )
        # return redirect('login') #本番用
    
        # ===== 管理者チェック =====
    if not current_user.is_admin:
        return redirect("teams:team_index")

    team_name = request.POST.get("team_name", "").strip()
    description = request.POST.get("team_description", "").strip()

    # 空チェック
    if not team_name:
        return redirect("teams:team_index")

    # 重複チェック
    if Teams.objects.filter(
        name=team_name,
        space=current_user.space
    ).exists():
        return redirect("teams:team_index")

    # 作成
    Teams.objects.create(
        name=team_name,
        description=description, 
        space=current_user.space,
        leader_user=None
    )

    return redirect("teams:team_index")


# @login_required  # ログイン機能実装後に有効化
@require_POST
def delete_team(request):

    # ===== 開発用 強制ユーザー取得 =====
    if getattr(request, "user", None) and request.user.is_authenticated:
        current_user = request.user
    else:
        current_user = get_object_or_404(
            User,
            pk="11111111-1111-1111-1111-222222222001"  # テスト用管理者
        )
        # return redirect('login') #本番用

    # ===== 管理者チェック =====
    if not current_user.is_admin:
        return redirect("teams:team_index")

    team_id = request.POST.get("team_id")

    if not team_id:
        return redirect("teams:team_index")

    # 同一spaceチェック付きで取得
    team = get_object_or_404(
        Teams,
        id=team_id,
        space=current_user.space
    )

    team_name = team.name  # メッセージ用に保存

    team.delete()

    return redirect("teams:team_index")

# @login_required  # ログイン機能実装後有効化
@require_POST
def edit_team(request):

    # ===== 開発用 強制ユーザー取得 =====
    if getattr(request, "user", None) and request.user.is_authenticated:
        current_user = request.user
    else:
        current_user = get_object_or_404(
            User,
            pk="11111111-1111-1111-1111-222222222001"  # テスト用管理者
        )
        # return redirect('login') #本番用

    # ===== 管理者チェック =====
    if not current_user.is_admin:
        return redirect("teams:team_index")

    team_id = request.POST.get("team_id")
    team_name = request.POST.get("team_name", "").strip()
    description = request.POST.get("team_description", "").strip()

    if not team_id:
        return redirect("teams:team_index")

    # ===== 対象チーム取得（同一spaceチェック） =====
    team = get_object_or_404(
        Teams,
        id=team_id,
        space=current_user.space
    )

    # ===== 空チェック =====
    if not team_name:
        return redirect("teams:team_index")

    # ===== 重複チェック（自分を除外） =====
    if Teams.objects.filter(
        name=team_name,
        space=current_user.space
    ).exclude(id=team_id).exists():
        return redirect("teams:team_index")

    # ===== 更新 =====
    team.name = team_name
    team.description = description
    team.save()

    return redirect(f"{reverse('teams:team_index')}?team_id={team.id}")

# @login_required  # ログイン機能実装後有効化
@require_POST
def add_member(request):

    # ===== 開発用 強制ユーザー取得 =====
    if getattr(request, "user", None) and request.user.is_authenticated:
        current_user = request.user
    else:
        current_user = get_object_or_404(
            User,
            pk="11111111-1111-1111-1111-222222222001"
        )
        # return redirect('login')  # 本番用

    if not current_user.is_admin:
        return HttpResponse(status=403)

    team_id = request.POST.get("team_id")
    user_id = request.POST.get("user_id")

    if not team_id or not user_id:
        return HttpResponse(status=400)

    team = get_object_or_404(
        Teams,
        id=team_id,
        space=current_user.space
    )

    user = get_object_or_404(User, id=user_id)

    # すでに所属しているかチェック
    if not Team_Users.objects.filter(team=team, user=user).exists():
        Team_Users.objects.create(team=team, user=user)

    # 通常のteamsページをそのまま返す
    teams = Teams.objects.all().order_by("created_at")
    selected_team = team
    team_members = Team_Users.objects.filter(team=team).select_related("user")

    context = {
        "teams": teams,
        "selected_team": selected_team,
        "team_members": team_members,
    }

    return render(request, "teams/teams.html", context)

# @login_required  # ログイン機能実装後有効化
@require_http_methods(["GET"])
def user_search(request):

    # 開発用ユーザー取得
    if request.user.is_authenticated:
        current_user = request.user
    else:
        current_user = get_object_or_404(
            User,
            pk="11111111-1111-1111-1111-222222222001"
        )
        # return redirect('login')  # 本番用

    query = request.GET.get("q", "").strip()
    team_id = request.GET.get("team_id")

    users = User.objects.filter(space=current_user.space)

    if query:
        users = users.filter(
            Q(name__icontains=query) |
            Q(employee_id__icontains=query)
        )

    context = {
        "users": users,
        "team_id": team_id,
    }

    return render(request, "teams/modals/result_list.html", context)


# ===== メンバー削除 =====
# @login_required  # ログイン機能実装後有効化
@require_POST
def delete_member(request):

    # ===== 開発用 ユーザー取得 =====
    if getattr(request, "user", None) and request.user.is_authenticated:
        current_user = request.user
    else:
        current_user = get_object_or_404(
            User,
            pk="11111111-1111-1111-1111-222222222001"  # テスト用管理者
        )
        # return redirect('login')  # 本番用

    # ===== 管理者チェック =====
    if not current_user.is_admin:
        return HttpResponse(status=403)

    # ===== POSTデータ取得 =====
    team_id = request.POST.get("team_id")
    user_id = request.POST.get("user_id")

    # ===== 必須チェック =====
    if not team_id or not user_id:
        return HttpResponse(status=400)

    # ===== チーム取得（space制限付き）=====
    team = get_object_or_404(
        Teams,
        id=team_id,
        space=current_user.space
    )

    # ===== チームメンバー紐付け取得 =====
    link = get_object_or_404(
        Team_Users,
        team=team,
        user_id=user_id
    )

    # ===== 削除実行 =====
    link.delete()

    # ===== 再描画用データ取得 =====
    team_members = Team_Users.objects.filter(
        team=team
    ).select_related("user")

    # ===== コンテキスト作成 =====
    context = {
        "teams": Teams.objects.filter(
            space=current_user.space
        ).order_by("created_at"),
        "selected_team": team,
        "team_members": team_members,
    }

    # ===== HTMX用：teams.htmlを返却（hx-selectで右側のみ更新）=====
    return render(request, "teams/teams.html", context)


# ===== リーダー設定 =====
# @login_required  # ログイン機能実装後有効化
@require_POST
def set_leader(request):

    # ===== 開発用 ユーザー取得 =====
    if getattr(request, "user", None) and request.user.is_authenticated:
        current_user = request.user
    else:
        current_user = get_object_or_404(
            User,
            pk="11111111-1111-1111-1111-222222222001"  # テスト用管理者
        )
        # return redirect('login')  # 本番用

    # ===== 管理者チェック =====
    if not current_user.is_admin:
        return HttpResponse(status=403)

    # ===== JSON受け取り =====
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return HttpResponse(status=400)

    team_id = payload.get("team_id")
    member_id = payload.get("member_id")

    if not team_id or not member_id:
        return HttpResponse(status=400)

    # ===== チーム取得（space制限付き）=====
    team = get_object_or_404(
        Teams,
        id=team_id,
        space=current_user.space
    )

    # ===== そのユーザーがそのチームのメンバーかチェック =====
    get_object_or_404(
        Team_Users,
        team=team,
        user_id=member_id
    )

    # ===== リーダー更新 =====
    new_leader = get_object_or_404(User, id=member_id)
    team.leader_user = new_leader
    team.save(update_fields=["leader_user", "updated_at"])

    return JsonResponse({"ok": True})
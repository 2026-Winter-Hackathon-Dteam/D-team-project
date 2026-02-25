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
from .forms import TeamCreateForm, TeamEditForm, AddMemberForm

User = get_user_model()

@require_http_methods(["GET"])
def set_current_team(request, team_id):
    return redirect(f"{reverse('teams:team_index')}?team_id={team_id}")


#@login_required # ログイン機能実装後に有効化
@require_http_methods(["GET"]) # 追記
def team_index(request):
    # ログインユーザー取得（未ログイン時はログイン画面に遷移、space所属確認の時に必要。）
    if getattr(request, "user", None) and request.user.is_authenticated:
        current_user = request.user
    else:
        current_user = get_object_or_404(User, pk="11111111-1111-1111-1111-222222222001") #テスト用ユーザー
        # return redirect('login') #本番用

    # チーム一覧取得
    teams = Teams.objects.filter(space=current_user.space).order_by("created_at")

    create_form = TeamCreateForm(space=current_user.space)

    # ユーザーがクリックしたチームのIDを取り出す
    # GETパラメータからteam_idを取得（なければNone）
    selected_team_id = request.GET.get("team_id")
    # 選択されたチームの初期値
    selected_team = None
    team_members = []

    # 選択されたチームのIDが取得されているならチームメンバー情報を取り出す
    if selected_team_id:
        selected_team = get_object_or_404(
            Teams,
            id=selected_team_id,
            space=current_user.space # 追記(5,同一space所属で見れるという権限チェックを追加する)
        )
        team_members = Team_Users.objects.filter(team=selected_team).select_related("user")
    
    context = {
        "teams": teams,
        "selected_team": selected_team,
        "team_members": team_members,
        "create_form": create_form,  
    }

    return render(request, "teams/teams.html", context)


# @login_required  # ログイン機能実装後に有効化
@require_POST
def create_team(request):

    # ===== 開発用ユーザー取得 =====
    if getattr(request, "user", None) and request.user.is_authenticated:
        current_user = request.user
    else:
        current_user = get_object_or_404(
            User,
            pk="11111111-1111-1111-1111-222222222001"
        )
        # return redirect('login') #本番用

    if not current_user.is_admin:
        return redirect("teams:team_index")

    form = TeamCreateForm(
        request.POST,
        space=current_user.space
    )

    if form.is_valid():
        team = form.save(commit=False)
        team.space = current_user.space
        team.leader_user = None
        team.save()
        return redirect("teams:team_index")

    # バリデーションエラー時
    teams = Teams.objects.filter(
        space=current_user.space
    ).order_by("created_at")

    return render(request, "teams/teams.html", {
        "teams": teams,
        "selected_team": None,
        "team_members": [],
        "create_form": form,
    })


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

    team = get_object_or_404(
        Teams,
        id=team_id,
        space=current_user.space
    )

    form = TeamEditForm(
        request.POST,
        instance=team,
        space=current_user.space
    )

    if form.is_valid():
        form.save()
        return redirect(f"{reverse('teams:team_index')}?team_id={team.id}")

    # エラー時
    teams = Teams.objects.filter(
        space=current_user.space
    ).order_by("created_at")

    team_members = Team_Users.objects.filter(
        team=team
    ).select_related("user")

    create_form = TeamCreateForm(space=current_user.space)

    return render(request, "teams/teams.html", {
        "teams": teams,
        "selected_team": team,
        "team_members": team_members,
        "create_form": create_form,
        "edit_form": form,
    })

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

    form = AddMemberForm(
        request.POST,
        current_user=current_user
    )

    if form.is_valid():
        form.save()
        team = form.team  # form内で保持している前提

        # ===== 再描画用データ =====
        teams = Teams.objects.filter(
            space=current_user.space
        ).order_by("created_at")

        selected_team = team

        team_members = Team_Users.objects.filter(
            team=selected_team
        ).select_related("user")

        context = {
            "teams": teams,
            "selected_team": selected_team,
            "team_members": team_members,
            "create_form": TeamCreateForm(space=current_user.space),
        }

        response = render(request, "teams/teams.html", context)

        response["HX-Trigger"] = "memberAdded"

        return response

    # ===== エラー時 =====
    teams = Teams.objects.filter(
        space=current_user.space
    ).order_by("created_at")

    selected_team = Teams.objects.filter(
        id=request.POST.get("team_id"),
        space=current_user.space
    ).first()

    team_members = Team_Users.objects.filter(
        team=selected_team
    ).select_related("user") if selected_team else []

    create_form = TeamCreateForm(space=current_user.space)

    return render(request, "teams/teams.html", {
        "teams": teams,
        "selected_team": selected_team,
        "team_members": team_members,
        "create_form": create_form,
        "add_member_form": form,
    })


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
# ===== 追加済判定用：対象チームに所属している user_id 一覧 =====
    selected_team_users = set()
    if team_id:
        team = get_object_or_404(
            Teams,
            id=team_id,
            space=current_user.space
        )
        selected_team_users = set(
            Team_Users.objects.filter(team=team).values_list("user_id", flat=True)
        )

    context = {
        "users": users,
        "team_id": team_id,
        "selected_team_users": selected_team_users,
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

    is_leader = str(team.leader_user_id) == str(user_id)

    # ===== チームメンバー紐付け取得 =====
    link = get_object_or_404(
        Team_Users,
        team=team,
        user_id=user_id
    )


    # ===== 削除実行 =====
    link.delete()

    # リーダー削除ならリーダー解除
    if is_leader:
        team.leader_user = None
        team.save(update_fields=["leader_user", "updated_at"])

        response = HttpResponse(status=204)
        response["HX-Redirect"] = f"{reverse('teams:team_index')}?team_id={team.id}"
        return response

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
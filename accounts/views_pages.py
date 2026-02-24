import secrets
import string
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.views.decorators.http import require_http_methods
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from .forms import  OwnerMemberCreateForm
from teams.models import Team_Users


# カスタムユーザークラスを取得
User = get_user_model()

# ***************************************************************************
class TopView(TemplateView):
    template_name = "accounts/top.html"


# ***************************************************************************
# 一般ユーザー作成
@login_required
def create_member(request):
    space=request.user.space

    # 作成ボタンが押された（POST）なら、登録処理を行う
    if request.method == "POST":
        form = OwnerMemberCreateForm(
            request.POST,
            space = space,
            user = request.user
        )

        if form.is_valid():
            # 新規作成ユーザー登録後の表示のためパスワードを変数に格納
            raw_password = generate_password()
            # 所属スペースの取得
            if space:
                # is_adminの取得
                if request.user == space.owner_user:
                    is_admin = form.cleaned_data.get("is_admin", False)
                else:
                    is_admin = False
                # DB登録処理
                try:
                    with transaction.atomic():
                        # ユーザー登録
                        user = User.objects.create_member(
                            space = space,
                            employee_id = form.cleaned_data["employee_id"],
                            password=raw_password,
                            name=form.cleaned_data["name"],
                            is_admin = is_admin
                        ) 
                        # チーム所属登録
                        teams = form.cleaned_data["teams"]
                        if teams:
                            Team_Users.objects.bulk_create([
                                Team_Users(user=user, team=team)
                                for team in teams
                            ])

                        # 登録成功画面の表示
                        context = {
                            'space_code': user.space.code,
                            'employee_id': user.employee_id,
                            'generated_password': raw_password
                        }
                        return render(request,"accounts/modals/create_member_success.html", context)
                    
                except IntegrityError:
                    form.add_error(None, "登録処理中にエラーが発生しました")

    # HTMXからのアクセス（GET）、POSTの処理に失敗時に入力フォームを返す
    else:
        form = OwnerMemberCreateForm(
            space = space,
            user = request.user
        )
    return render(request, "accounts/modals/create_member_form.html", {"form": form})


# ***************************************************************************
# メンバー表示
@login_required
def members(request):
    space=request.user.space
    query = request.GET.get("q", "").strip()
    
    # メンバー一覧取得
    space_members = (
        User.objects
        .filter(space=space)
        .prefetch_related("team_users_set__team")
    )
    # 検索がある場合だけ絞り込み(名前または社員IDの部分一致)
    if query:
        space_members = space_members.filter(
            Q(name__icontains=query) |
            Q(employee_id__icontains=query)
        )

    context = {
        "space":space,
        "space_members": space_members,
    }
    return render(request, "accounts/members.html", context)

# ***************************************************************************
@login_required
def profile(request):
    return render(request, "accounts/profile.html")

@login_required
def edit_member(request):
    return render(request, "accounts/edit_member.html")

@login_required
def change_password(request):
    return render(request, "accounts/change_password.html")


# ***************************************************************************
# ランダムパスワードの生成
def generate_password(length=10):
    chars=string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars)for _ in range(length))
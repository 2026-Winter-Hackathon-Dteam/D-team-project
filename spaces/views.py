from django.shortcuts import render
from django.http import HttpResponse
from .models import Spaces
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404, redirect
from django.db import transaction
from django.http import HttpResponseForbidden
from django.contrib.auth import get_user_model

def sample(request):
    return HttpResponse("")

# spaceとowner編集画面表示 (GET)
# @login_required
@require_http_methods(["GET"])
def space_edit_get(request):
    # 現在のユーザーのスペースを取得（1ユーザー = 1スペース想定）
    if getattr(request, "user", None) and request.user.is_authenticated:
        current_user = request.user
    else:
        current_user = get_object_or_404(get_user_model(), pk="11111111-1111-1111-1111-222222222001")  # テスト用ユーザー
    
    space = get_object_or_404(Spaces, owner_user=current_user)
    
    # current_user がスペースのオーナーであることを確認
    if current_user != space.owner_user:
        return HttpResponseForbidden("オーナーしかスペースを編集できません。")
    
    context = {
        "space": space
    }
    return render(request, "spaces/add_space.html", context)

# space編集 (space名) (POST)
# @login_required
@require_http_methods(["POST"])
def space_edit_post(request):
    # 現在のユーザーのスペースを取得（1ユーザー = 1スペース想定）
    if getattr(request, "user", None) and request.user.is_authenticated:
        current_user = request.user
    else:
        current_user = get_object_or_404(get_user_model(), pk="11111111-1111-1111-1111-222222222001")  # テスト用ユーザー
    
    space = get_object_or_404(Spaces, owner_user=current_user)
    
    # current_user がスペースのオーナーであることを確認
    if current_user != space.owner_user:
        return HttpResponseForbidden("オーナーしかスペースを編集できません。")
    
    new_name = request.POST.get("name")
    space.name = new_name
    space.save(update_fields=["name"])
    
    return redirect('accounts:top')  # スペース編集後の遷移先は要検討(トップページ？)
    

#　owner変更




# space削除
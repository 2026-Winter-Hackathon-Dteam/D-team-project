from django.shortcuts import render
from django.http import HttpResponse
from .models import Spaces
from .forms import SpaceEditForm, SpaceOwnerChangeForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404, redirect
from django.db import transaction
from django.http import HttpResponseForbidden
from django.contrib.auth import get_user_model

def sample(request):
    return HttpResponse("")

# spaceとowner編集画面表示 (GET)と編集処理 (POST)
@login_required
@require_http_methods(["GET", "POST"])
def space_edit(request, space_id):
    # 現在のユーザーのスペースを取得（1ユーザー = 1スペース想定）
    current_user = request.user
    
    space = get_object_or_404(Spaces, owner_user=current_user)
    
    # current_user がスペースのオーナーであることを確認
    if current_user != space.owner_user:
        return HttpResponseForbidden("オーナーしかスペースを編集できません。")
    
    target = get_object_or_404(Spaces, id=space_id)
    
    # スペースに所属するメンバーを取得
    User = get_user_model()
    members = User.objects.filter(space=space).order_by('name')
    
    if request.method == "POST":
        form = SpaceEditForm(request.POST, instance=target)
        owner_form = SpaceOwnerChangeForm(space, request.POST)
        
        if form.is_valid():
            with transaction.atomic():
                form.save()
                # オーナー変更処理
                if owner_form.is_valid():
                    new_owner_id = owner_form.cleaned_data.get('owner_id')
                    if new_owner_id:
                        new_owner = get_object_or_404(User, id=new_owner_id)
                        space.owner_user = new_owner
                        space.save(update_fields=['owner_user'])
            return redirect('analysis:personal_analysis')  # personal_analysis.htmlへリダイレクト（後で修正）
    else:
        form = SpaceEditForm(instance=target)
        owner_form = SpaceOwnerChangeForm(space)
    
    context = {
        "form": form,
        "owner_form": owner_form,
        "space": space,
        "members": members,
    }
    return render(request, "spaces/add_space.html", context)


# space削除
@login_required
@require_http_methods(["POST"])
@transaction.atomic
def space_delete(request, space_id):
    
    current_user = request.user
    
    space = get_object_or_404(Spaces, id=space_id)
    
    # current_user がスペースのオーナーであることを確認
    if current_user != space.owner_user:
        return redirect('spaces:space_edit', space_id=space_id)  # オーナーでない場合は編集ページへリダイレクト
    
    if request.method == "POST":
        space.owner_user = None
        space.save(update_fields=['owner_user'])
        space.users.all().delete()
        space.delete()
        return redirect('accounts:top') # トップページへリダイレクト
    
    return redirect('spaces:space_edit', space_id=space_id)  # GETリクエストは編集ページへリダイレクト
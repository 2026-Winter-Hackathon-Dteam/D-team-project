from django.shortcuts import render, redirect
from django.views.generic import TemplateView


# ***************************************************************************
# testコード
def test_create_member(request):
    # HTMXからのアクセス（GET）なら、入力フォームを返す
    if request.method == "GET":
        return render(request, "accounts/modals/create_member_form.html")

    # 作成ボタンが押された（POST）なら、成功画面を返す
    if request.method == "POST":
        context = {
            'space_code': 'DTM',
            'employee_id': '12345',
            'generated_password': 'tm9je!&ne8s1',
        }
        return render(request, "accounts/modals/create_member_success.html", context)


# ***************************************************************************
class TopView(TemplateView):
    template_name = "accounts/top.html"

def members(request):
        return render(request, "accounts/members.html", {
        "team_list": [],
    })

def profile(request):
    return render(request, "accounts/profile.html")

def edit_member(request):
    return render(request, "accounts/edit_member.html")

def change_password(request):
    return render(request, "accounts/change_password.html")
from django.shortcuts import render
from django.http import HttpResponse

def sample(request):
    # return render(request, "accounts/modals/create_member.html", {
    # return render(request, "accounts/modals/create_member_success.html", {
    return render(request, "accounts/members.html", {
        "team_list": [],
    })

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
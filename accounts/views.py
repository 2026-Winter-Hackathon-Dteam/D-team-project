from django.shortcuts import render
from django.http import HttpResponse

def sample(request):
    # return HttpResponse("")
    return render(request, "accounts/members.html")
# 画面表示テスト用にHttpRespomseをコメントアウトしてrenderに変更中（削除予定）
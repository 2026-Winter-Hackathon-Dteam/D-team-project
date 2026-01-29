from django.shortcuts import render
from django.http import HttpResponse

def sample(request):
    # return HttpResponse("")
    return render(request, "sample.html")  # 画面表示テスト用にHttpRespomseをコメントアウトしてrenderへ 削除予定

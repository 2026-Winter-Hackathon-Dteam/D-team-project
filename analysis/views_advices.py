from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse

from accounts.models import CustomUser
from .models import UserAdvice


#　アドバイス表示（ユーザー）
#@login_required
@require_http_methods(["GET"])
def get_user_advice(request):

    user = get_object_or_404(CustomUser, pk="11111111-1111-1111-1111-222222222001")
    #user = request.user # 本番用

    advices = UserAdvice.objects.filter(user=user).values(
        "value_key__name",
        "importance",
        "is_minus_side",
        "advice_text"
    )

    advice_list = [
        {
            "value_key": a["value_key__name"],
            "importance": a["importance"],
            "advice": a["advice_text"]
        }
        for a in advices
    ]

    return JsonResponse({
        "advices": advice_list
    })


#　結果表示/アドバイス取得（チーム）
#@login_required
@require_http_methods(["GET"])
def get_team_advice(request, team_id):
    return print("チームのアドバイスです")

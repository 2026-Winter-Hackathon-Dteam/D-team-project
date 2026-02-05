from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from accounts.models import CustomUser
from .models import UserValueScore
from django.db.models import (
    F, FloatField, ExpressionWrapper,
    Case, When, Value, CharField, BooleanField,
    OuterRef, Subquery)
from django.db.models.functions import Abs


#　アドバイス表示（ユーザー）
#@login_required
@require_http_methods(["GET"])
def get_user_advice(request):

    user = get_object_or_404(CustomUser, pk="11111111-1111-1111-1111-222222222001")
    #user = request.user # 本番用

    team_id = "aaa11111-1111-1111-1111-111111111111"  # テスト用チームID
    #team_id = request.GET.get("team_id") # 本番用
    
    # value_key_id ごとに最新のIDを取得
    latest_ids = (
        UserValueScore.objects
        .filter(user=user)
        .values('value_key_id')
        .annotate(latest_id=Subquery(
            UserValueScore.objects
            .filter(user=user, value_key_id=OuterRef('value_key_id'))
            .order_by('-created_at', '-id')
            .values('id')[:1]
        ))
    )
    
    # メモリ内で処理
    latest_user_scores = UserValueScore.objects.filter(
        id__in=[s['latest_id'] for s in latest_ids]
    ).select_related('value_key')
    
    results_data = {}
    for score in latest_user_scores:
        value_key_id = score.value_key_id
        
        # team_meanを取得
        from .models import TeamValueScore
        team_score = TeamValueScore.objects.filter(
            team_id=team_id,
            value_key_id=value_key_id
        ).first()
        
        if team_score:
            team_mean = team_score.mean
            diff = score.personal_score - team_mean
            
            # importanceを判定
            if diff >= 6:
                importance = "high"
            elif diff >= 3:
                importance = "middle"
            else:
                importance = "low"
            
            # is_minusを判定
            is_minus = score.personal_score < 0
            
            # アドバイスを取得
            from .models import UserAdvice
            advice = UserAdvice.objects.filter(
                value_key_id=value_key_id,
                importance=importance,
                is_minus_side=is_minus
            ).first()
            
            advice_text = advice.advice_text if advice else ""
            
            results_data[str(value_key_id)] = {
                "value_key_id": str(value_key_id),
                "personal_score": score.personal_score,
                "team_mean": team_mean,
                "diff": diff,
                "importance": importance,
                "advice_text": advice_text
            }
    
    user_advices = list(results_data.values())

    return JsonResponse(
        {"user_advices": user_advices},
        json_dumps_params={'ensure_ascii': False}
    )


#　結果表示/アドバイス取得（チーム）
#@login_required
@require_http_methods(["GET"])
def get_team_advice(request, team_id):
    return print("チームのアドバイスです")

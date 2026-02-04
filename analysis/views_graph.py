from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.db.models import OuterRef, Subquery

from accounts.models import CustomUser
from .models import UserValueScore, TeamValueScore


# 結果表示（ユーザー）
#@login_required
@require_http_methods(["GET"])
def results(request):
    """診断結果を表示するページ（ユーザーのみ）"""
    # テスト用ユーザー
    user = get_object_or_404(CustomUser, pk="11111111-1111-1111-1111-222222222001")
    team_id = "aaa11111-1111-1111-1111-111111111111"

    # 最新のUserValueScoreを取得
    latest_scores = (
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

    latest_user_scores = UserValueScore.objects.filter(
        id__in=[s['latest_id'] for s in latest_scores]
    ).select_related('value_key')

    # データをメモリで処理
    results_data = {}
    for score in latest_user_scores:
        value_key_id = score.value_key_id

        # team_meanを取得
        team_score = TeamValueScore.objects.filter(
            team_id=team_id,
            value_key_id=value_key_id
        ).first()

        if team_score:
            team_mean = team_score.mean
            diff = score.personal_score - team_mean
            results_data[str(value_key_id)] = {
                "value_key_id": str(value_key_id),
                "value_key_name": score.value_key.value_key,
                "personal_score": score.personal_score,
                "team_mean": team_mean,
                "diff": diff
            }

    diffs = list(results_data.values())

    context = {
        "graph_data": diffs
    }
    return render(request, "analysis/members_page.html", context)


#　グラフ表示データ取得（ユーザー）
#@login_required
@require_http_methods(["GET"])
def get_user_graph(request):

    # テスト用ユーザー（users.json の最初のユーザー）
    user = get_object_or_404(CustomUser, pk="11111111-1111-1111-1111-222222222001")
    #user = request.user # 本番用

    #チームを指定
    #team_id = request.GET.get("team_id")
    team_id = "aaa11111-1111-1111-1111-111111111111"  # テスト用チームID
    if not team_id:
        return redirect("analysis:results")

    # 最新のUserValueScoreを取得
    latest_scores = (
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

    latest_user_scores = UserValueScore.objects.filter(
        id__in=[s['latest_id'] for s in latest_scores]
    ).select_related('value_key')

    # データをメモリで処理
    results_data = {}
    for score in latest_user_scores:
        value_key_id = score.value_key_id

        # team_meanを取得
        team_score = TeamValueScore.objects.filter(
            team_id=team_id,
            value_key_id=value_key_id
        ).first()

        if team_score:
            team_mean = team_score.mean
            diff = score.personal_score - team_mean
            results_data[str(value_key_id)] = {
                "value_key_id": str(value_key_id),
                "personal_score": score.personal_score,
                "team_mean": team_mean,
                "diff": diff
            }

    diffs = list(results_data.values())

    return JsonResponse({"results": list(diffs)})

from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
import json
from django.http import JsonResponse
from django.db.models import OuterRef, Subquery
from accounts.models import CustomUser
from .models import UserValueScore, TeamValueScore
from teams.models import Teams, Team_Users


# ユーザースコア取得（ユーザースコアのみ）
def _get_user_scores_only(user):
    """ユーザーの最新スコアのみを取得"""
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
        results_data[str(value_key_id)] = {
            "value_key_id": str(value_key_id),
            "value_key_name": score.value_key.value_key,
            "personal_score": score.personal_score
        }

    return list(results_data.values())


# ユーザースコア取得（チーム比較込み）
def _get_user_scores_with_team(user, team_id):
    """ユーザーのスコア＋チーム比較データを取得"""
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
            diff = abs(score.personal_score - team_mean)
            results_data[str(value_key_id)] = {
                "value_key_id": str(value_key_id),
                "value_key_name": score.value_key.value_key,
                "personal_score": score.personal_score,
                "team_mean": team_mean,
                "diff": diff
            }
        print(f"[DEBUG] UserValueScore: {score}, TeamValueScore: {team_score}")
    return list(results_data.values())


# ユーザーグラフデータ取得（チーム所属あり対応）
#@login_required
@require_http_methods(["GET", "POST"])
def get_user_graph(request):
    """ユーザースコア＋チーム比較データを返すAPI"""
    # テスト用ユーザー
    user = get_object_or_404(CustomUser, pk="11111111-1111-1111-1111-222222222001")
    #user = request.user # 本番用

    # チームを指定（必須）
    team_id = request.GET.get("team_id")
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            team_id = data.get("team_id") or team_id
        except Exception:
            pass
    if not team_id:
        #team_id = "aaa11111-1111-1111-1111-111111111111"  # テスト用チームID
        return redirect('analysis:personal_analysis')  # チーム未指定ならpersonal_analysisへリダイレクト

    diffs = _get_user_scores_with_team(user, team_id=team_id)
    print(f"[DEBUG] User graph data: {diffs}")  # デバッグ用出力
    
    return JsonResponse({"results": diffs})

# チームスコア取得
def _get_team_scores(team_id):
    """チームの最新スコアを取得"""
    latest_scores = (
        TeamValueScore.objects
        .filter(team_id=team_id)
        .values('value_key_id')
        .annotate(latest_id=Subquery(
            TeamValueScore.objects
            .filter(team_id=team_id, value_key_id=OuterRef('value_key_id'))
            .order_by('-created_at', '-id')
            .values('id')[:1]
        ))
    )

    latest_team_scores = TeamValueScore.objects.filter(
        id__in=[s['latest_id'] for s in latest_scores]
    ).select_related('value_key')

    results_data = {}
    for score in latest_team_scores:
        value_key_id = score.value_key_id
        results_data[str(value_key_id)] = {
            "value_key_id": str(value_key_id),
            "value_key_name": score.value_key.value_key,
            "mean": score.mean,
            "max_diff": score.max_diff,
            "std": score.std,
        }

    return list(results_data.values())


# マトリクスグラフ表示データ取得（チーム）
#@login_required
@require_http_methods(["GET", "POST"])
def get_team_matrixgraph(request):
    """チームのグラフデータを取得する（API用）"""
    
    # チームを指定（必須）
    team_id = request.GET.get("team_id")
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            team_id = data.get("team_id") or team_id
        except Exception:
            pass
    if not team_id:
        return redirect('analysis:personal_analysis')  # チーム未指定なら個人分析ページへリダイレクト

    # ログインユーザー取得（未ログイン時はテスト用ユーザー）
    if getattr(request, "user", None) and request.user.is_authenticated: #本番では、getattr(・・・None)は外しても良い
        current_user = request.user
    else:
        current_user = get_object_or_404(CustomUser, pk="11111111-1111-1111-1111-222222222001") #テスト用ユーザー
        #return redirect("analysis:login")  # 未ログインならログインページへ（本番用）

    team = get_object_or_404(Teams, pk=team_id)
    is_team_leader = team.leader_user_id == current_user.id

    diffs = _get_team_scores(team_id=team_id) if is_team_leader else []

    print(f"[DEBUG] Team graph data: {diffs}")  # デバッグ用出力

    return JsonResponse({"results": diffs})

# 散布図グラフデータ取得（チーム）
def _get_team_scatter_data(team_id):
    """チームの散布図グラフデータを取得"""
    team_scores = _get_team_scores(team_id=team_id)
    team_mean_map = {
        item["value_key_id"]: item["mean"]
        for item in team_scores
    }
    value_key_name_map = {
        item["value_key_id"]: item["value_key_name"]
        for item in team_scores
    }

    # チームに所属するユーザー一覧を取得
    team_users = Team_Users.objects.filter(team_id=team_id).select_related('user')

    value_buckets = {
        value_key_id: {
            "value_key_id": value_key_id,
            "value_key_name": value_key_name_map.get(value_key_id),
            "team_mean": team_mean_map.get(value_key_id),
            "users": [],
        }
        for value_key_id in team_mean_map.keys()
    }

    for team_user in team_users:
        user = team_user.user
        user_scores = _get_user_scores_only(user)
        for score in user_scores:
            value_key_id = score["value_key_id"]
            bucket = value_buckets.get(value_key_id)
            if not bucket:
                bucket = {
                    "value_key_id": value_key_id,
                    "value_key_name": score.get("value_key_name"),
                    "team_mean": team_mean_map.get(value_key_id),
                    "users": [],
                }
                value_buckets[value_key_id] = bucket

            bucket["users"].append({
                "user_id": str(user.id),
                "user_name": user.name,
                "personal_score": score["personal_score"],
            })

    return list(value_buckets.values())

# 散布図グラフ表示データ取得（チーム分析）
#@login_required
@require_http_methods(["GET", "POST"])
def get_team_scatter_graph(request):
    """チームの散布図グラフデータを取得する（API用）"""
    
    # チームを指定（必須）
    team_id = request.GET.get("team_id")
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            team_id = data.get("team_id") or team_id
        except Exception:
            pass
    if not team_id:
        return redirect('analysis:personal_analysis')  # チーム未指定なら個人分析ページへリダイレクト

    # ログインユーザー取得（未ログイン時はテスト用ユーザー）
    if getattr(request, "user", None) and request.user.is_authenticated: #本番では、getattr(・・・None)は外しても良い
        current_user = request.user
    else:
        current_user = get_object_or_404(CustomUser, pk="11111111-1111-1111-1111-222222222001") #テスト用ユーザー
        #return redirect("analysis:login")  # 未ログインならログインページへ（本番用）

    team = get_object_or_404(Teams, pk=team_id)
    is_team_leader = team.leader_user_id == current_user.id

    scatter_data = _get_team_scatter_data(team_id=team_id) if is_team_leader else []

    print(f"[DEBUG] Team scatter graph data: {scatter_data}")  # デバッグ用出力

    return JsonResponse({"results": scatter_data})
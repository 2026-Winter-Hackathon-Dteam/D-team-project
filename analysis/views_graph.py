from django.db.models import OuterRef, Subquery
from .models import UserValueScore, TeamValueScore
from teams.models import Team_Users


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

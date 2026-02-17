from django.db.models import OuterRef, Subquery
from .models import UserValueScore, TeamValueScore
from teams.models import Team_Users

THEORETICAL_MIN = -12
THEORETICAL_MAX = 12
RANGE = THEORETICAL_MAX - THEORETICAL_MIN
MAX_DIFF_THEORETICAL_MAX = 24

# スコアを0-100に正規化
def normalize_score(score):
    return (score - THEORETICAL_MIN) / RANGE * 100

# 標準偏差を0-100に正規化(0<=std<=12の想定)
def normalize_std(std_value):
    return std_value / THEORETICAL_MAX * 100

# 最大差を0-100に正規化（0<=max_diff<=24の想定）
def normalize_max_diff(diff):
    return diff / MAX_DIFF_THEORETICAL_MAX * 100


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
        raw_score = score.personal_score
        results_data[str(value_key_id)] = {
            "value_key_id": str(value_key_id),
            "personal_score": raw_score, 
            "personal_score_normalized": normalize_score(raw_score),
        }
        
    order = ["context", "feedback", "persuasion", "hierarchy", "decision", "trust", "conflict", "time"]
    order_index = {key: index for index, key in enumerate(order)}
    sorted_list = sorted(results_data.values(), key=lambda x: order_index.get(x['value_key_id'], 999))

    return list(sorted_list)

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
            raw_score = score.personal_score
            results_data[str(value_key_id)] = {
                "value_key_id": str(value_key_id),
                "personal_score_normalized": normalize_score(raw_score),
                "team_mean": team_mean,
                "team_mean_normalized": normalize_score(team_mean),
            }
            
        order = ["context", "feedback", "persuasion", "hierarchy", "decision", "trust", "conflict", "time"]
        order_index = {key: index for index, key in enumerate(order)}
        sorted_list = sorted(results_data.values(), key=lambda x: order_index.get(x['value_key_id'], 999))

        print(f"[DEBUG] UserValueScore: {score}, TeamValueScore: {team_score}")
    return list(sorted_list)

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
        max_diff_normalized = normalize_max_diff(score.max_diff)
        std_normalized = normalize_std(score.std)
        results_data[str(value_key_id)] = {
            "value_key_id": str(value_key_id),
            "value_key_name": score.value_key.value_key,
            "mean": score.mean,
            "max_diff_normalized": max_diff_normalized,
            "std_normalized": std_normalized,
        }

    order = ["context", "feedback", "persuasion", "hierarchy", "decision", "trust", "conflict", "time"]
    order_index = {key: index for index, key in enumerate(order)}
    sorted_list = sorted(results_data.values(), key=lambda x: order_index.get(x['value_key_id'], 999))

    return list(sorted_list)

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
            "team_mean_raw": team_mean_map.get(value_key_id),  # 生のスコアを追加
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
                    "team_mean_raw": team_mean_map.get(value_key_id),  # ここにも追加
                    "users": [],
                }
                value_buckets[value_key_id] = bucket

            raw_score = score["personal_score"]
            team_mean_raw = bucket["team_mean_raw"]

            team_mean = team_mean_map.get(value_key_id)
            diff = None
            if team_mean is not None:
                diff = abs(raw_score - team_mean_raw)
            
            bucket["users"].append({
                "user_id": str(user.id),
                "user_name": user.name,
                "personal_score_normalized": normalize_score(raw_score),
                "diff_normalized": normalize_score(diff) if diff is not None else None,
            })
            
            order = ["context", "feedback", "persuasion", "hierarchy", "decision", "trust", "conflict", "time"]
            order_index = {key: index for index, key in enumerate(order)}
            sorted_list = sorted(value_buckets.values(), key=lambda x: order_index.get(x['value_key_id'], 999))

    return list(sorted_list)
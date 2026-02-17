from .models import UserValueScore
from django.db.models import (
    OuterRef, Subquery)
from .models import TeamValueScore, UserAdvice, TeamAdvice


#　アドバイス取得（ユーザー）
# チーム比較込みのアドバイスデータを作成
def _get_user_advices_with_team(user, team_id):
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
        team_score = TeamValueScore.objects.filter(
            team_id=team_id,
            value_key_id=value_key_id
        ).first()

        if team_score:
            team_mean = team_score.mean
            diff = abs(score.personal_score - team_mean)

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
            advice = UserAdvice.objects.filter(
                value_key_id=value_key_id,
                importance=importance,
                is_minus_side=is_minus
            ).first()

            advice_text = advice.advice_text if advice else ""

            results_data[str(value_key_id)] = {
                "value_key_id": str(value_key_id),
                "importance": importance,
                "advice_text": advice_text
            }
            order = ["context", "feedback", "persuasion", "hierarchy", "decision", "trust", "conflict", "time"]
            order_index = {key: index for index, key in enumerate(order)}
            sorted_list = sorted(results_data.values(), key=lambda x: order_index.get(x['value_key_id'], 999))

    return list(sorted_list)

# アドバイス取得（チーム）
def _get_team_advices(team_id):
    # チームの最新スコアを取得
    latest_ids = (
        TeamValueScore.objects
        .filter(team_id=team_id)
        .values('value_key_id')
        .annotate(latest_id=Subquery(
            TeamValueScore.objects
            .filter(
                team_id=OuterRef('team_id'),
                value_key_id=OuterRef('value_key_id')
            )
            .order_by('-created_at', '-id')
            .values('id')[:1]
        ))
    )

    latest_team_scores = TeamValueScore.objects.filter(
        id__in=[s['latest_id'] for s in latest_ids]
    ).select_related('value_key', 'team')

    # データをメモリで処理
    results_data = {}
    for score in latest_team_scores:
        value_key_id = score.value_key_id

        std_dev = score.std
        max_diff = abs(score.max_diff)

        # それぞれのvalue_keyごとにcodeを判定
        if std_dev < 3 and max_diff < 6:
            code = "Q1_stable_harmony"
        elif std_dev < 3 and max_diff >= 6:
            code = "Q2_deep_focus"
        elif std_dev >= 3 and max_diff < 6:
            code = "Q3_partial_diversity"
        else:
            code = "Q4_wide_diversity"

        # アドバイスを取得
        advice = TeamAdvice.objects.filter(
            value_key_id=value_key_id,
            code=code
        ).first()

        results_data[str(value_key_id)] = {
            "value_key_id": str(value_key_id),
            "code": code,
            "situation_text": advice.situation_text if advice else "",
            "summary_text": advice.summary_text if advice else "",
            "detail_text": advice.detail_text if advice else "",
        }
        order = ["context", "feedback", "persuasion", "hierarchy", "decision", "trust", "conflict", "time"]
        order_index = {key: index for index, key in enumerate(order)}
        sorted_list = sorted(results_data.values(), key=lambda x: order_index.get(x['value_key_id'], 999))


    return list(sorted_list)

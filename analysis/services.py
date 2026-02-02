from collections import defaultdict
from statistics import pstdev
from .models import UserValueScore, TeamValueScore


def recalc_team_scores(team_id):

    #1チーム分の統計を再計算

    scores = UserValueScore.objects.filter(
    user__team_users__team_id=team_id
    )

    grouped = defaultdict(list)

    for s in scores:
        grouped[s.value_key_id].append(s.personal_score)

    # 保存用オブジェクト作成
    team_objs = []

    for value_key, values in grouped.items():

        mean = sum(values) / len(values)
        max_diff = max(values) - min(values)
        std = pstdev(values) if len(values) > 1 else 0 # データが1つしかない場合、標準偏差は0とする

        team_objs.append(
            TeamValueScore(
                team_id=team_id,
                value_key_id=value_key,
                mean=mean,
                max_diff=max_diff,
                std=std,
            )
        )

    # チームスコア保存
    TeamValueScore.objects.bulk_create(team_objs)

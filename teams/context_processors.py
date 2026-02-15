from teams.models import Team_Users

def team_context(request):
    """全ページでチーム情報を使えるようにする"""
    if not request.user.is_authenticated:
        return {
            'teams': [],
            'current_team': None
        }

    # ユーザーが所属するチーム一覧
    teams = Team_Users.objects.filter(
        user=request.user
    ).select_related('team').values_list('team', flat=True)
    
    teams_list = list(teams)

    # セッションから現在のチームを取得
    current_team_id = request.session.get('current_team_id')
    current_team = None
    
    if current_team_id and current_team_id in [str(t) for t in teams_list]:
        from teams.models import Teams
        current_team = Teams.objects.filter(id=current_team_id).first()
    elif teams_list:
        # 未設定なら最初のチームを選択
        from teams.models import Teams
        current_team = Teams.objects.filter(id=teams_list[0]).first()

    return {
        'teams': Teams.objects.filter(id__in=teams_list),
        'current_team': current_team
    }
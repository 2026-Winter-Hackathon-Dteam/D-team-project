from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.http import JsonResponse
import json
import sys
from accounts.models import CustomUser
from teams.models import Team_Users, Teams
from .models import UserValueScore, Question
from .services import recalc_team_scores
from .views_graph import _get_user_scores_only, _get_user_scores_with_team, _get_team_scores, _get_team_scatter_data
from .views_advices import _get_user_advices_with_team, _get_team_advices


# 回答保存　submit_answersを1回実行すると、SQLへのクエリは3+N回（Nはユーザーが所属するチーム数）
#@login_required
@require_http_methods(["POST"])
@transaction.atomic
def submit_answers(request):

    print(f"[DEBUG] submit_answers called - Method: {request.method}")

    # 回答受け取る
    try:
        data = json.loads(request.body.decode("utf-8"))
        answers = data.get("answers", {})
        print(f"[DEBUG] Parsed answers: {answers}")
    except Exception as e:
        print(f"[DEBUG] JSON parsing error: {e}")
        return JsonResponse({"error": "invalid json"}, status=400)

    print("ANSWERS:", answers) # saveAnswers()動いているか確認用

    if not answers:
        return JsonResponse({"error": "no answers"}, status=400)

    # ログインユーザー取得（未ログイン時はテスト用ユーザー）
    if getattr(request, "user", None) and request.user.is_authenticated: #本番では、getattr(・・・None)は外しても良い 
        user = request.user
    else:
        user = get_object_or_404(CustomUser, pk="11111111-1111-1111-1111-222222222001")
        #return redirect("analysis:login")  # 未ログインならログインページへ（本番用）


    # Questionからまとめて取得（id,value_key,is_reverse）
    questions = Question.objects.filter(
        id__in=answers.keys()
    ).values(
        "id",
        "value_key_id",
        "is_reverse"
    )

    # 取得したクエリセットをインデックス化する
    question_map = {
        str(q["id"]): q
        for q in questions
    }

    # 集計用
    value_totals = {}  # value_key → 合計点

    for question_id, raw_score in answers.items():

        q = question_map.get(question_id)
        if not q:
            return JsonResponse({"error": f"invalid question_id: {question_id}"}, status=400)

        # 逆転処理
        score = int(raw_score)
        if q["is_reverse"]:
            score *= -1

        value_key = q["value_key_id"]

        # valueごとにscoreを足していく
        value_totals[value_key] = value_totals.get(value_key, 0) + score

    # 集計結果から保存オブジェクト作成
    objs = [
        UserValueScore(
            user=user,
            value_key_id=value_key,
            personal_score=total_score
        )
        for value_key, total_score in value_totals.items()
    ]

    print(f"[DEBUG] UserValueScore objects to save: {len(objs)}")
    print(f"[DEBUG] value_totals: {value_totals}")
    print(f"[DEBUG] First object to save: user={objs[0].user if objs else 'N/A'}, value_key_id={objs[0].value_key_id if objs else 'N/A'}, personal_score={objs[0].personal_score if objs else 'N/A'}")
    sys.stdout.flush()

    # DB保存
    try:
        result = UserValueScore.objects.bulk_create(objs)
        print(f"[DEBUG] bulk_create succeeded, saved {len(result)} objects")
    except Exception as e:
        print(f"[ERROR] bulk_create failed: {e}")
        return JsonResponse({"error": f"DB save failed: {e}"}, status=500)

    # チームスコア再計算
    team_ids = Team_Users.objects.filter(
        user=user
    ).values_list("team_id", flat=True)

    for team_id in team_ids:
        recalc_team_scores(team_id)

    # セッションの質問リスト削除
    request.session.pop("question_ids", None)

    print(f"[DEBUG] submit_answers returning success")

    # POST処理完了後、personal_analysisのURLをJSONで返す
    return JsonResponse({"redirect_url": "/analysis/personal_analysis/"})


# members_pageビュー
#@login_required
@require_http_methods(["GET", "POST"])
def members_page(request):
    """
    価値観公開しているユーザーの評価結果ページを表示（GET）
    グラフデータをコンテキストに含める
    """
    # ログインユーザー取得（未ログイン時はテスト用ユーザー）
    if getattr(request, "user", None) and request.user.is_authenticated: #本番では、getattr(・・・None)は外しても良い 
        current_user = request.user
    else:
        current_user = get_object_or_404(CustomUser, pk="11111111-1111-1111-1111-222222222002")
        #return redirect("analysis:login")  # 未ログインならログインページへ（本番用）

    target_user_id = "11111111-1111-1111-1111-222222222001" # テスト用ユーザーID
    #target_user_id = request.GET.get("user_id") # 本番用
    if not target_user_id or str(current_user.id) == target_user_id:
        return redirect("analysis:personal_analysis")

    # 同一スペースの他ユーザーのみ表示可能
    user = get_object_or_404(
        CustomUser,
        pk=target_user_id,
        space_id=current_user.space_id,
    )

    # target_user_idのユーザー名取得
    target_user_name = user.name

    # グラフデータ取得
    scores = _get_user_scores_only(user)
    
    # value_key_id と personal_score のみにフィルタリング
    graph_data = [
        {
            "value_key_id": item["value_key_id"],
            "personal_score": item["personal_score"]
        }
        for item in scores
    ]

    context = {
        "target_user_name": target_user_name,
        "graph_data": graph_data,
    }
    
    print(f"[DEBUG] Rendering members_page with context: {context}")
    
    return render(request, "analysis/members_page.html", context)


# personal_analysisビュー
#@login_required
@require_http_methods(["GET"])
def personal_analysis(request):
    """チーム比較＋アドバイス表示ページ（GET）"""
    team_id = request.GET.get("team_id", "")

    # ログインユーザー取得（未ログイン時はテスト用ユーザー）
    if getattr(request, "user", None) and request.user.is_authenticated: #本番では、getattr(・・・None)は外しても良い 
        user = request.user
    else:
        user = get_object_or_404(CustomUser, pk="11111111-1111-1111-1111-222222222001")
        #return redirect("analysis:login")  # 未ログインならログインページへ（本番用）
        

    team_options = [
        {
            "id": str(team_user.team_id),
            "name": team_user.team.name,
        }
        for team_user in Team_Users.objects.filter(user=user).select_related("team")
    ]

    # チーム未選択時はスコアのみ表示、ユーザーがteamに所属していなければ、チーム選択前にリダイレクト
    if not team_id:
        graph_data = _get_user_scores_only(user)
        advice_data = []
        is_team_leader = False
    else:
        is_member = Team_Users.objects.filter(user=user, team_id=team_id).exists()
        if not is_member:
            return redirect("analysis:personal_analysis")
        graph_data = _get_user_scores_with_team(user, team_id=team_id)
        advice_data = _get_user_advices_with_team(user, team_id=team_id)
        is_team_leader = Teams.objects.filter(id=team_id, leader_user_id=user.id).exists()
    context = {
        "team_id": team_id,
        "graph_data": graph_data,
        "advice_data": advice_data,
        "teams": team_options,
        "is_team_leader": is_team_leader,
    }
    print(f"[DEBUG] Rendering personal_analysis with context: {context}")
    return render(request, "analysis/personal_analysis.html", context)


# managers_pageビュー
#@login_required
@require_http_methods(["GET", "POST"])
def managers_page(request):
    """チームマネージャー向けページ表示"""
    team_id = request.GET.get("team_id", "")

    # ログインユーザー取得（未ログイン時はテスト用ユーザー）
    if getattr(request, "user", None) and request.user.is_authenticated: #本番では、getattr(・・・None)は外しても良い 
        current_user = request.user
    else:
        current_user = get_object_or_404(CustomUser, pk="11111111-1111-1111-1111-222222222001")
        #return redirect("analysis:login")  # 未ログインならログインページへ（本番用）

    team = get_object_or_404(Teams, pk=team_id)
    is_team_leader = team.leader_user_id == current_user.id

    team_scores = _get_team_scores(team_id=team_id) if is_team_leader else []
    team_advice = _get_team_advices(team_id=team_id) if is_team_leader else []
    team_matrixdata = (
        [
            {
                "value_key_id": d.get("value_key_id"),
                "x": d.get("max_diff"),
                "y": d.get("std"),
            }
            for d in team_scores
        ]
        if is_team_leader
        else []
    )
    team_scatter_data = _get_team_scatter_data(team_id=team_id) if is_team_leader else []
    l_team_scatter_data = (
        [
            {
                "value_key_id": d.get("value_key_id"),
                "x": d.get("personal_score"),
                "y": d.get("team_mean"),
            }
            for d in team_scatter_data # TODO 確認
        ]
        if is_team_leader
        else []
    )
    
    print(f"[DEBUG] Team graph data: {team_scores}")  # デバッグ用出力
    print(f"[DEBUG] Team advice data: {team_advice}")  # デバッグ用出力
    print(f"[DEBUG] Team scatter data: {l_team_scatter_data}")  # デバッグ用出力
    print(f"[DEBUG] Team matrix data: {team_matrixdata}")  # デバッグ用出力

    context = {
        "team_id": team_id,
        "team_graph_data": team_scores,
        "team_advice_data": team_advice,
        "team_scatter_data": l_team_scatter_data,
        "is_team_leader": is_team_leader,
        "team_matrix_data": team_matrixdata,
    }

    return render(request, "analysis/managers_page.html", context)
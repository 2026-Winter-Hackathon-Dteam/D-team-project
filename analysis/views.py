from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .models import ValueMaster, UserValueScore, TeamValueScore, UserAdvice, TeamAdvice, Question
from accounts.models import CustomUser
from .forms import QuestionForm
from django.db import transaction
from django.http import JsonResponse
import json
import sys
from uuid import UUID
import random
from teams.models import Team_Users
from .services import recalc_team_scores
from django.db.models import F, FloatField, ExpressionWrapper, OuterRef, Subquery



def questions_index(request):
    # ページ番号指定なしでアクセスされた場合は1ページ目へリダイレクト
    return redirect('analysis:question_page', page=1)

#テスト用
def index(request):
    return HttpResponse("INDEX OK")


QUESTIONS_PER_PAGE = 6  # ページ数は自由に設定可

# 質問取得
#@login_required
@require_http_methods(["GET"])
def question_page(request, page):
    
    # 初回アクセス時だけシャッフル生成
    if "question_ids" not in request.session:

        ids = list(
            Question.objects
            .filter(is_active=True)
            .values_list("id", flat=True)
        )

        random.shuffle(ids)

        # セッションは JSON シリアライズされるため UUID を文字列化して保存する
        request.session["question_ids"] = [str(i) for i in ids]

    # セッションから順序取得
    ids = request.session["question_ids"]

    # セッションから取り出した文字列を UUID に戻してクエリに渡す
    ids_uuid = [UUID(pk) for pk in ids]

    # DB から全件取得してマッピング用に保持
    questions = Question.objects.filter(id__in=ids_uuid)
    
    # id -> Question オブジェクトのマッピングを作成
    question_map = {str(q.id): q for q in questions}
    
    # セッションの順序に従って並べ替える
    questions_ordered = [question_map[pk] for pk in ids if pk in question_map]

    paginator = Paginator(questions_ordered, QUESTIONS_PER_PAGE)
    page_obj = paginator.get_page(page)

    context = {
        "page_obj": page_obj,
        "total_pages": paginator.num_pages,
    }

    return render(request, "analysis/questions.html", context)
    
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

    # テスト用ユーザー（users.json の最初のユーザー）
    user = get_object_or_404(CustomUser, pk="11111111-1111-1111-1111-222222222001")
    #user = request.user # 本番用

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
    
    # 結果返す 
    return JsonResponse({
        "status": "ok",
        "totals": value_totals,
    })


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
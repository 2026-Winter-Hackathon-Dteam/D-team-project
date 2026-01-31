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
from django.db.models import Case, When
from uuid import UUID
import random

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

    # Case/Whenで順序維持
    preserved = Case(
        *[When(id=pk, then=pos) for pos, pk in enumerate(ids_uuid)]
    )

    questions = Question.objects.filter(id__in=ids_uuid).order_by(preserved)

    paginator = Paginator(questions, QUESTIONS_PER_PAGE)
    page_obj = paginator.get_page(page)

    context = {
        "page_obj": page_obj,
        "total_pages": paginator.num_pages,
    }

    return render(request, "analysis/questions.html", context)
    
# 回答保存
#@login_required
@require_http_methods(["POST"])
@transaction.atomic
def submit_answers(request):

    # 回答受け取る
    data = json.loads(request.body)
    answers = data["answers"]
    print("ANSWERS:", answers) # saveAnswers()動いているか確認用
    #user = request.user
    user = get_object_or_404(CustomUser, pk=1)  # テスト用（ユーザーID=1固定）

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
        
        q = question_map[question_id]

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

    # DB保存
    UserValueScore.objects.bulk_create(objs)

    return JsonResponse({
        "status": "ok",
        "totals": value_totals,  # 必要なら返す
    })



# スコア計算



# 結果表示（ユーザー）


# 結果表示（チーム）


#　アドバイス取得（ユーザー、チーム）
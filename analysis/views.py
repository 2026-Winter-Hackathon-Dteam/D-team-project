from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .models import ValueMaster, UserValueScore, TeamValueScore, UserAdvice, TeamAdvice, Question
from .forms import QuestionForm
from django.db import transaction
from django.http import JsonResponse
import json

#テスト用
def index(request):
    return HttpResponse("INDEX OK")


QUESTIONS_PER_PAGE = 8  # ページ数は自由に設定可

# 質問取得
#@login_required
@require_http_methods(["GET"])
def question_page(request, page):
    questions = (
        Question.objects.filter(is_active=True).order_by("?")
    )
    paginator = Paginator(questions, QUESTIONS_PER_PAGE)
    page_obj = paginator.get_page(page)
    
    context = {
        "page_obj": page_obj, #1ページ分の質問
        "total_pages": paginator.num_pages, #全体ページ数
    }

    return render(request, "analysis/questions.html", context)


# 回答保存
"""
@login_required
@require_http_methods(["POST"])
@transaction.atomic
def submit_answers(request):
    #json受け取り
    data = json.loads(request.body)
    answers = data["answers"]
    user = request.user
    

    question_map = {
        str(q.id): q.value_key_id
        for q in Question.objects.filter(id__in=answers.keys())
    }

    #保存用リスト
    objs = []
    
    for question_id, score in answers.items():
        objs.append(
            UserValueScore(
                user=user,
                value_key_id=question_map[question_id],
                personal_score=int(score)
            )
        )

    UserValueScore.objects.bulk_create(objs)
    #js側に成功通知を送る
    return JsonResponse({"status": "ok"})
"""


# スコア計算



# 結果表示（ユーザー）


# 結果表示（チーム）


#　アドバイス取得（ユーザー、チーム）
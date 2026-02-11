from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from uuid import UUID
import random
from .models import Question


#テスト用
def index(request):
    # return HttpResponse("INDEX OK")
    return render(request, "analysis/fe-personal_analysis.html")

QUESTIONS_PER_PAGE = 6  # ページ数は自由に設定可


# ページ番号指定なしでアクセスされた場合は1ページ目へリダイレクト
def questions_index(request):
    return redirect('analysis:question_page', page=1)


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

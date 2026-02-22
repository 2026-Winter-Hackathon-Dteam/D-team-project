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
    return render(request, "analysis/personal_analysis.html")

QUESTIONS_PER_PAGE = 6  # ページ数は自由に設定可


# ページ番号指定なしでアクセスされた場合は1ページ目へリダイレクト
def questions_index(request):
    return redirect('analysis:question_page', page=1)


# questions_startは質問開始前のページ
#login_required
@require_http_methods(["GET"])
def questions_start(request):
    return render(request, "analysis/questions_start.html")


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

        print(f"[DEBUG] is_active=True の質問数: {len(ids)}")
        print(f"[DEBUG] 質問IDs: {ids}")

        random.shuffle(ids)

        # セッションは JSON シリアライズされるため UUID を文字列化して保存する
        request.session["question_ids"] = [str(i) for i in ids]

    # セッションから順序取得
    ids = request.session["question_ids"]
    print(f"[DEBUG] セッションから取得した質問IDs: {ids}")

    # セッションから取り出した文字列を UUID に戻してクエリに渡す
    ids_uuid = [UUID(pk) for pk in ids]
    print(f"[DEBUG] UUID変換後: {ids_uuid}")

    # DB から全件取得してマッピング用に保持
    questions = Question.objects.filter(id__in=ids_uuid)
    print(f"[DEBUG] DBから取得した質問数: {questions.count()}")

    # id -> Question オブジェクトのマッピングを作成
    question_map = {str(q.id): q for q in questions}
    print(f"[DEBUG] question_mapのキー数: {len(question_map)}")

    # セッションの順序に従って並べ替える
    questions_ordered = [question_map[pk] for pk in ids if pk in question_map]
    print(f"[DEBUG] 並べ替え後の質問数: {len(questions_ordered)}")

    paginator = Paginator(questions_ordered, QUESTIONS_PER_PAGE)
    page_obj = paginator.get_page(page)

    print(f"[DEBUG] Page: {page}, Total pages: {paginator.num_pages}")
    print(f"[DEBUG] Questions on this page: {len(page_obj.object_list)}")
    print(f"[DEBUG] Page object: {page_obj.object_list}")

    context = {
        "page_obj": page_obj,
        "total_pages": paginator.num_pages,
    }

    return render(request, "analysis/questions.html", context)

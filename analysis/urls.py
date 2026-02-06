from django.urls import path
from . import views

app_name = "analysis"

urlpatterns = [
    path('', views.index, name='index'),
    path('questions/', views.questions_index, name='questions_index'),
    path("questions/<int:page>/", views.question_page, name="question_page"),
    path("answers/", views.submit_answers, name="submit_answers"),
    path("members_page/", views.members_page, name="members_page"),
    path("graphs/me/", views.get_user_graph, name="get_user_graph"),
    path("personal_analysis/", views.personal_analysis, name="personal_analysis"),
    path("advices/me/", views.get_user_advice, name="get_user_advice"),
]
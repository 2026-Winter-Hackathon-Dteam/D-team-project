from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path("questions/<int:page>/", views.question_page, name="question_page"),
    path("answers/", views.submit_answers, name="submit_answers"),
]
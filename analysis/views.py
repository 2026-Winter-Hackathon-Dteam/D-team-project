from .views_questions import index, questions_index, question_page
from .views_answers import submit_answers
from .views_graph import results, get_user_graph
from .views_advices import get_user_advice, get_team_advice

__all__ = [
    "index",
    "questions_index",
    "question_page",
    "submit_answers",
    "results",
    "get_user_graph",
    "get_user_advice",
    "get_team_advice",
]
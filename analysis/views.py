from .views_questions import index, questions_index, question_page
from .views_answers import submit_answers, members_page
from .views_graph import get_user_graph
from .views_advices import get_user_advice, get_team_advice

__all__ = [
    "index",
    "questions_index",
    "question_page",
    "submit_answers",
    "members_page",
    "get_user_graph",
    "get_user_advice",
    "get_team_advice",
]
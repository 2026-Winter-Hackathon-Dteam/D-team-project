from .views_questions import index, questions_index, question_page
from .views_answers import submit_answers, members_page, personal_analysis, managers_page
from .views_graph import get_user_graph, get_team_matrixgraph
from .views_advices import get_user_advice, get_team_advice

__all__ = [
    "index",
    "questions_index",
    "question_page",
    "submit_answers",
    "members_page",
    "personal_analysis",
    "get_user_graph",
    "get_team_matrixgraph",
    "get_user_advice",
    "get_team_advice",
    "managers_page",
]
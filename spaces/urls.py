from django.urls import path
from .views import sample, space_edit_get, space_edit_post


urlpatterns = [
    path('sample/', sample),
    path('edit/', space_edit_get, name='space_edit'),  # GET
    path('edit/', space_edit_post),  # POST
]
from django.urls import path
from .views import sample, space_edit
from .forms import SpaceEditForm


urlpatterns = [
    path('sample/', sample),
    path('edit/', space_edit, name='space_edit'),  # GET
    #path('edit/', space_edit_post),  # POST
]
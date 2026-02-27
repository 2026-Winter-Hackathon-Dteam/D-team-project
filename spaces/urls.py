from django.urls import path
from .views import sample, space_edit, space_delete_confirm,space_delete
from .forms import SpaceEditForm

app_name = "spaces"

urlpatterns = [
    path('sample/', sample),
    path('edit/<uuid:space_id>/', space_edit, name='space_edit'),
    path('delete_confirm/<uuid:space_id>/', space_delete_confirm, name='space_delete_confirm'),
    path('delete/<uuid:space_id>/', space_delete, name='space_delete'),
]
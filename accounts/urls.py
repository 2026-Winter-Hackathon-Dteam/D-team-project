from django.urls import path
from . import views_pages
from .views_auth import OwnerSignupView, CustomLoginView, CustomLogoutView
from .views_pages import CustomPasswordChangeView
from .views_pages import TopView


app_name = "accounts"

urlpatterns = [
    path('top/',TopView.as_view(), name='top'), 
    path('signup/', OwnerSignupView.as_view(), name='signup'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path('members/', views_pages.members , name='members'),
    path('create-member/', views_pages.create_member, name='create_member'),
    path('edit_member/<uuid:pk>/', views_pages.edit_member , name='edit_member'),
    path('profile/', views_pages.profile , name='profile'),
    path('change_password/', CustomPasswordChangeView.as_view(), name='change_password'),
]
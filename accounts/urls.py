from django.urls import path
from . import views_pages
from .views_auth import OwnerSignupView, OwnerMemberCreateView, CustomLoginView, CustomLogoutView
from .views_pages import TopView


app_name = "accounts"

urlpatterns = [
    # アカウント作成モーダルテスト用
    path('create-member/', views_pages.test_create_member, name='create_member'),
    path('top/',TopView.as_view(), name='top'), 
    path('login/', CustomLoginView.as_view(), name='login'),
    path('signup/', OwnerSignupView.as_view(), name='signup'),
    #path('create_member/', OwnerMemberCreateView.as_view(), name='create_member'),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path('members/', views_pages.members , name='members'),
    path('profile/', views_pages.profile , name='profile'),
    path('edit_member/', views_pages.edit_member , name='edit_member'),
    path('change_password/', views_pages.change_password , name='change_password'),
]
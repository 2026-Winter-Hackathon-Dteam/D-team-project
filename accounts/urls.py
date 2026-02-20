from django.urls import path
from . import views 

app_name = 'accounts'

urlpatterns = [
    path('sample/', views.sample, name='members'),
    # アカウント作成モーダルテスト用
    path('create-member/', views.test_create_member, name='create_member'),
]
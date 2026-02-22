from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from config import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('spaces/', include('spaces.urls')),
    path('teams/', include('teams.urls')),
    path('analysis/', include('analysis.urls', namespace='analysis')),
    path('', RedirectView.as_view(url='/top/'), name='root'),
    path('health/', views.health_check),
]

# Tailwind.CSS 動作確認のための開発環境用static配信設定（DEBUG=True時のみ有効）
if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATICFILES_DIRS[0],
    )

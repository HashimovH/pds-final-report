from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name="home"),
    path('analyze', views.analyze_full, name='analyze')
]
if settings.DEBUG:
    # This is nesseccary to access image files on the frontend
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

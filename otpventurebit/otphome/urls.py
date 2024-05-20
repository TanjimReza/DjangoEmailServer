
from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('', views.index, name='index'),
    path('hx', views.hx, name='hx'),
    path('bandwidth', views.bandwidth_log, name='bandwidth_log'),
] +  static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

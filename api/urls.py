from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api import views

router = DefaultRouter()
router.register('user', views.UserModelView, basename='user'),
router.register('group', views.GroupModelView, basename='group'),
router.register('pixpics', views.PixelPicsModelView, basename='pixpics'),
router.register('link', views.CreateLink, basename='link'),


urlpatterns = [
    path('', include((router.urls, 'api'))),
]

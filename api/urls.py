from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api import views

router = DefaultRouter()
router.register('user', views.UserModelView, basename='user'),
router.register('image', views.ImageModelView, basename='image')
router.register('group', views.GroupModelView, basename='group'),

urlpatterns = [
    path('', include((router.urls, 'api'))),
]

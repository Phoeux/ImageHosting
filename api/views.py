import json

from django.contrib.auth.models import User, Group
from django.db.models.query import QuerySet
from django.http import HttpResponse

from rest_framework import viewsets

from api.models import Image
from api.serializers import UserSerializer, ImageSerializer, GroupSerializer


class UserModelView(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects


class ImageModelView(viewsets.ModelViewSet):
    queryset = Image.objects
    serializer_class = ImageSerializer

    def get_queryset(self):
        queryset = self.request.user.image_set
        if isinstance(queryset, QuerySet):
            queryset = queryset.all()
        return queryset

    def create(self, request, *args, **kwargs):
        image = request.data['image']
        name = request.data['name']
        Image.objects.create(name=name, image=image, owner=self.request.user)
        return HttpResponse(json.dumps({'message': "Uploaded"}), status=200)


class GroupModelView(viewsets.ModelViewSet):
    queryset = Group.objects
    serializer_class = GroupSerializer

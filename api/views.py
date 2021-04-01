from django.contrib.auth.models import User, Group
from django.db.models.query import QuerySet
from django.urls import reverse

from rest_framework import viewsets
from rest_framework.response import Response

from api.models import Image, SmallPixPics
from api.serializers import UserSerializer, ImageSerializer, GroupSerializer, PixPicsSerializer


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
        basic, created = Group.objects.get_or_create(name='Basic')
        premium, created = Group.objects.get_or_create(name='Premium')
        enterprise, created = Group.objects.get_or_create(name='Enterprise')
        image = request.data['image']
        name = request.data['name']
        created_image = Image.objects.create(name=name, image=image, owner=self.request.user)

        if self.request.user in basic.user_set.all():
            return Response(request.build_absolute_uri(reverse("api:smpixpics-list")))
        if self.request.user in premium.user_set.all() or self.request.user.is_superuser:
            return Response([request.build_absolute_uri(reverse("api:smpixpics-list")),
                             request.build_absolute_uri(reverse("api:lgpixpics-list"))])
        if self.request.user in enterprise.user_set.all():
            return Response([request.build_absolute_uri(reverse("api:smpixpics-list")),
                             request.build_absolute_uri(reverse("api:lgpixpics-list"))])


class GroupModelView(viewsets.ModelViewSet):
    queryset = Group.objects
    serializer_class = GroupSerializer


class SmallPixelPicsModelView(viewsets.ModelViewSet):
    queryset = SmallPixPics.objects
    serializer_class = PixPicsSerializer

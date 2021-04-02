from django.contrib.auth.models import User, Group, Permission

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from thumbnails.models import ThumbnailMeta

from api.models import PixPics, EnterpriseLinks
from api.serializers import UserSerializer, GroupSerializer, PixPicsSerializer, BasicUserPixPicsSerializer, \
    LinkSerializer, ThumbnailSerializer


class UserModelView(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects
    permission_classes = [IsAuthenticated]


class GroupModelView(viewsets.ModelViewSet):
    queryset = Group.objects
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def create(self, request, *args, **kwargs):
        administrator, created = Group.objects.get_or_create(name='administrator')
        if self.request.user in administrator.user_set.all() or self.request.user.is_superuser:
            perm_1 = Permission.objects.get(codename='add_enterpriselinks')
            perm_2 = Permission.objects.get(codename='add_pixpics')
            perm_3 = Permission.objects.get(codename='add_thumbnailmeta')
            request.data['permissions'] = [perm_1.id, perm_2.id, perm_3.id]
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        return Response("Forbidden, user must be an admin", status=status.HTTP_403_FORBIDDEN)


class PixelPicsModelView(viewsets.ModelViewSet):
    queryset = PixPics.objects
    serializer_class = PixPicsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = self.request.user.pixpics_owner
        return queryset

    def list(self, request, *args, **kwargs):
        basic, created = Group.objects.get_or_create(name='Basic')
        queryset = self.filter_queryset(self.get_queryset())
        perm = Permission.objects.get(codename='add_pixpics')
        if self.request.user in basic.user_set.all() or self.request.user not in Group.permissions.through.objects.get(
                group_id=self.request.user.groups.get().id, permission_id=perm.id).group.user_set.all():
            serializer = BasicUserPixPicsSerializer(queryset, many=True, context={"request": request})
        else:
            serializer = self.get_serializer(queryset, many=True, context={"request": request})
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        basic, created = Group.objects.get_or_create(name='Basic')
        premium, created = Group.objects.get_or_create(name='Premium')
        enterprise, created = Group.objects.get_or_create(name='Enterprise')
        serializer = self.get_serializer(data=request.data)
        if not int(request.data['owner']) == self.request.user.id:
            return Response('Wrong owner')
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        pix = PixPics.objects.get(id=serializer.data['id'])
        if self.request.user in basic.user_set.all():
            response = Response(request.build_absolute_uri(pix.image.thumbnails.small.url))
            return response
        if self.request.user in premium.user_set.all() or enterprise.user_set.all():
            return Response([request.build_absolute_uri(pix.image.thumbnails.small.url),
                             request.build_absolute_uri(pix.image.thumbnails.large.url)])
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class CreateLink(viewsets.ModelViewSet):
    queryset = EnterpriseLinks.objects
    serializer_class = LinkSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        enterprise, created = Group.objects.get_or_create(name='Enterprise')
        if self.request.user in enterprise.user_set.all() or self.request.user.is_superuser or \
                self.request.user in Group.permissions.through.objects.filter(permission_id=37):
            if int(request.data['expire_time']) < 300 or int(request.data['expire_time']) > 30000:
                return Response('Expire time must be between 300 and 30 000 secs')
            req_img = PixPics.objects.get(id=request.data['img_link'])
            return Response(request.build_absolute_uri(f"/media/{req_img.image}/"))
        return Response("Forbidden, change your account to Enterprise", status=status.HTTP_403_FORBIDDEN)


class PlanCreate(viewsets.ModelViewSet):
    queryset = Group.objects
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        administrator, created = Group.objects.get_or_create(name='administrator')
        if self.request.user in administrator.user_set.all() or self.request.user.is_superuser:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        return Response("Forbidden, user must be an admin", status=status.HTTP_403_FORBIDDEN)


class ThumbnailModelView(viewsets.ModelViewSet):
    queryset = ThumbnailMeta.objects
    serializer_class = ThumbnailSerializer

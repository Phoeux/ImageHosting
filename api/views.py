from django.contrib.auth.models import User, Permission

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from api.models import PixPics, EnterpriseLinks, AccountType
from api.serializers import UserSerializer, GroupSerializer, PixPicsSerializer, BasicUserPixPicsSerializer, \
    LinkSerializer


class UserModelView(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects
    permission_classes = [IsAuthenticated, IsAdminUser]


class GroupModelView(viewsets.ModelViewSet):
    queryset = AccountType.objects
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def create(self, request, *args, **kwargs):
        if not AccountType.objects.filter(name='administrator').exists():
            administrator, _ = AccountType.objects.get_or_create(name='administrator')
            administrator.permissions.set(Permission.objects.all())

        administrator = AccountType.objects.get(name='administrator')
        if administrator.user_set.filter(id=self.request.user.id).exists() or self.request.user.is_superuser:
            perm_1 = Permission.objects.get(codename='add_enterpriselinks')
            perm_2 = Permission.objects.get(codename='add_pixpics')
            perm_3 = Permission.objects.get(codename='add_thumbnailmeta')
            if request.data['name'] == 'Premium' or request.data['name'] == 'Enterprise':
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
        queryset = self.filter_queryset(self.get_queryset())
        perm = Permission.objects.get(codename='add_pixpics')
        if not self.request.user.groups.get().permissions.filter(id=perm.id).exists():
            serializer = BasicUserPixPicsSerializer(queryset, many=True, context={"request": request})
        else:
            serializer = self.get_serializer(queryset, many=True, context={"request": request})
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not int(request.data['owner']) == self.request.user.id:
            return Response('Wrong owner')
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        pix = PixPics.objects.get(id=serializer.data['id'])
        perm = Permission.objects.get(codename='add_thumbnailmeta')
        if not self.request.user.groups.get().permissions.filter(id=perm.id).exists():
            response = Response(request.build_absolute_uri(pix.image.thumbnails.small.url))
            return response
        if self.request.user.groups.get().permissions.filter(id=perm.id).exists():
            return Response([request.build_absolute_uri(pix.image.thumbnails.small.url),
                             request.build_absolute_uri(pix.image.thumbnails.large.url)])
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class CreateLink(viewsets.ModelViewSet):
    queryset = EnterpriseLinks.objects
    serializer_class = LinkSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        perm = Permission.objects.get(codename='add_enterpriselinks')
        if self.request.user.groups.get().permissions.filter(id=perm.id).exists() or self.request.user.is_superuser:
            if int(request.data['validity_seconds']) < 300 or int(request.data['validity_seconds']) > 30_000:
                return Response('Expire time must be between 300 and 30 000 secs')
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            req_img = PixPics.objects.get(id=request.data['img_link'])
            return Response(request.build_absolute_uri(f"/media/{req_img.image}/"), status=status.HTTP_201_CREATED)
        return Response("Forbidden, change your account to Enterprise", status=status.HTTP_403_FORBIDDEN)

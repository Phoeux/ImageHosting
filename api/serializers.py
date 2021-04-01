from django.contrib.auth.models import User, Group
from rest_framework import serializers

from api.models import Image, PixPics


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ('name', 'image')


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'


class PixPicsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PixPics
        fields = '__all__'
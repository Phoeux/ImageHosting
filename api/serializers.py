from django.contrib.auth.models import User
from rest_framework import serializers
from time import time

from api.models import PixPics, EnterpriseLinks, AccountType


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountType
        fields = '__all__'


class BasicUserPixPicsSerializer(serializers.ModelSerializer):
    small_thumb = serializers.SerializerMethodField()

    class Meta:
        model = PixPics
        fields = ['id', 'owner', 'small_thumb']

    def get_small_thumb(self, instance):
        return self.context['request'].build_absolute_uri(instance.image.thumbnails.small.url)


class PixPicsSerializer(BasicUserPixPicsSerializer):
    large_thumb = serializers.SerializerMethodField()

    class Meta:
        model = PixPics
        fields = ['id', 'image', 'owner', 'small_thumb', 'large_thumb']

    def get_large_thumb(self, instance):
        return self.context['request'].build_absolute_uri(instance.image.thumbnails.large.url)


class LinkSerializer(serializers.ModelSerializer):
    expire_time = serializers.SerializerMethodField()

    class Meta:
        model = EnterpriseLinks
        fields = ['id', 'validity_seconds', 'img_link', 'expire_time']

    def get_expire_time(self, data):
        return self.validate_expire_time(data)

    def validate_expire_time(self, data):
        validity_seconds = data.validity_seconds
        time_stamp = data.time_stamp
        curr_time = time()
        if time_stamp + validity_seconds >= curr_time:
            expire_time = (time_stamp + time_stamp) - curr_time
            return expire_time
        else:
            data.delete()
            raise serializers.ValidationError

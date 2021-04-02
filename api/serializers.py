from django.contrib.auth.models import User, Group
from rest_framework import serializers

from api.models import PixPics, EnterpriseLinks


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'


class PixPicsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PixPics
        fields = ['id', 'image', 'owner', 'expire_time']

    def to_representation(self, instance):
        basic, created = Group.objects.get_or_create(name='Basic')
        data = super().to_representation(instance)
        data['small_thumb'] = self.context['request'].build_absolute_uri(instance.image.thumbnails.small.url)
        if self.context['request'].user not in basic.user_set.all():
            data['large_thumb'] = self.context['request'].build_absolute_uri(instance.image.thumbnails.large.url)
        return data


class BasicUserPixPicsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PixPics
        fields = ['id', 'owner']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['small_thumb'] = self.context['request'].build_absolute_uri(instance.image.thumbnails.small.url)
        return data


class LinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnterpriseLinks
        fields = ['id', 'expire_time', 'img_link']

    def to_internal_value(self, data):
        if data['expire_time'] > 30_000 or data['expire_time'] < 300:
            raise serializers.ValidationError("Expire time must be between 300 and 30 000 secs")
        return data
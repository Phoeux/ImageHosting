from django.contrib.auth.models import User
from django.db import models
from thumbnails.fields import ImageField
from time import time


class PixPics(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pixpics_owner')
    image = ImageField()


class EnterpriseLinks(models.Model):
    time_stamp = models.PositiveIntegerField(default=time)
    expire_time = models.PositiveIntegerField(default=300)
    img_link = models.ForeignKey(PixPics, on_delete=models.CASCADE, related_name='links')

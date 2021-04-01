from django.contrib.auth.models import User
from django.db import models
from thumbnails.fields import ImageField


class Image(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField()

    def __str__(self):
        return self.name


class PixPics(models.Model):
    image = ImageField(pregenerated_sizes=["small", "large"])


class SmallPixPics(models.Model):
    image = ImageField(pregenerated_sizes=["small"])


class BigPixPics(models.Model):
    image = ImageField(pregenerated_sizes=["large"])

from django.contrib.auth.models import User
from django.db import models


def nameFile(instance, filename):
    return '/'.join(['images', str(instance.name), filename])


class Image(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField()

    def __str__(self):
        return self.name

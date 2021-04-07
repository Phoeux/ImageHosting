from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import models
from thumbnails.fields import ImageField
from time import time
from PIL import Image

User = get_user_model()


class PixPics(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pixpics_owner')
    image = ImageField()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        img = Image.open(self.image.path)

        if AccountType.objects.get(id=self.owner_id):
            height = AccountType.objects.get(id=self.owner_id).thumb_height
            width = AccountType.objects.get(id=self.owner_id).thumb_width
            output_size = (width, height)
            if output_size != (None, None):
                img.thumbnail(output_size)
                img.save(f"{self.image.path.split('.')[0]}_customsize.jpg")


class EnterpriseLinks(models.Model):
    time_stamp = models.PositiveIntegerField(default=time)
    validity_seconds = models.PositiveIntegerField(default=300)
    img_link = models.ForeignKey(PixPics, on_delete=models.CASCADE, related_name='links')


class AccountType(Group):
    thumb_width = models.PositiveIntegerField(blank=True, null=True)
    thumb_height = models.PositiveIntegerField(blank=True, null=True)

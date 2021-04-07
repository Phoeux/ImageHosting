import tempfile

from PIL import Image
from django.contrib.auth.models import Group, User
from django.urls import reverse
from rest_framework import status

from rest_framework.test import APITestCase

from api.models import PixPics


class TestAPI(APITestCase):
    def setUp(self):
        self.user = User.objects.create_superuser('joe', 'joe@doe.com', 'doe')

    def test_group_creation(self):
        # Unauthorizer user can't create groups
        url = reverse('api:group-list')
        data = {
            "name": "test_group"
        }
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, msg=response.data)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # Admin creat group
        self.client.login(username='joe', password='doe')
        data = {
            "name": "test_group"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, msg=response.data)

    def test_upload_image_for_unauthorized_user(self):
        # Creation of image
        image = Image.new('RGB', (100, 100))
        tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        image.save(tmp_file)
        tmp_file.seek(0)
        # Unauthorized user can't upload an image
        url = reverse('api:pixpics-list')
        data = {'image': tmp_file,
                'owner': self.user.id
                }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        response = self.client.get(url, format='json')
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_file_is_accepted(self):
        self.client.force_authenticate(self.user)
        # Creation of image
        image = Image.new('RGB', (100, 100))
        tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        image.save(tmp_file)
        tmp_file.seek(0)
        # Authorized user can upload an image
        url = reverse('api:pixpics-list')
        data = {
            'image': tmp_file,
            'owner': self.user.id
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        response = self.client.get(url, format='json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        print(PixPics.objects.all())
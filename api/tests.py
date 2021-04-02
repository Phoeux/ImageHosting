import tempfile

import PIL
from django.contrib.auth.models import Group, User
from django.urls import reverse
from rest_framework import status

from rest_framework.test import APITestCase



class TestAPI(APITestCase):
    def setUp(self):
        self.user = User.objects.create_superuser('joe', 'joe@doe.com', 'doe')
        self.user2 = User.objects.create_user('joe2', 'joe@doe.com', 'doe')
        self.basic_group = Group.objects.create(name='Basic')
        self.premium_group = Group.objects.create(name='Premium')
        self.enterprise_group = Group.objects.create(name='Enterprise')

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

    def test_upload_image(self):
        # Creation of an image
        image = PIL.Image.new('RGB', size=(1, 1))
        file = tempfile.NamedTemporaryFile(suffix='.jpg')
        image.save(file)
        # sending image
        self.client.login(username='joe', password='doe')
        url = reverse('api:pixpics-list')
        with open(file.name, 'rb') as f:
            data = {
                'image': f,
                'owner': self.user
            }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)




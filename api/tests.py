import tempfile

from PIL import Image
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status

from rest_framework.test import APITestCase

from api.models import AccountType


class TestAPI(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser('joe', 'joe@doe.com', 'doe')
        self.user2 = get_user_model().objects.create_user('joe2', 'joe2@doe.com', 'doe2')
        basic = AccountType.objects.create(name='Basic')
        enterprise = AccountType.objects.create(name='Enterprise')
        basic.user_set.add(self.user2)
        enterprise.user_set.add(self.user)

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
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        response = self.client.get(url, format='json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_link_creation(self):
        # Unauthorized user can't create a link
        url = reverse('api:link-list')
        data ={
            'validity_seconds': 200,
            'img_link': 1
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, msg=response.data)
        # Unauthorized user can't get any info about links
        response = self.client.get(url, format='json')
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        # Creation of Image
        self.client.force_authenticate(self.user)
        image = Image.new('RGB', (100, 100))
        tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        image.save(tmp_file)
        tmp_file.seek(0)
        url = reverse('api:pixpics-list')
        data = {
            'image': tmp_file,
            'owner': self.user.id
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        # Enterprise group user or user in any other group with permissions can create links
        url_link = reverse('api:link-list')
        data_link = {
            'validity_seconds': 300,
            'img_link': 1
        }
        response = self.client.post(url_link, data_link, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, msg=response.data)
        # Users can't create links with wrong validity seconds, have to be from 300 to 30_000
        data_link_wrong_valid_secs = {
            'validity_seconds': 200,
            'img_link': 1
        }
        response = self.client.post(url_link, data_link_wrong_valid_secs, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.data)
        # Enterprise group user or user in any other group with permissions can get info about links
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.data)
        self.client.logout()
        # Basic group user or user in any other group without permissions can't create links
        self.client.force_authenticate(self.user2)
        data_link = {
            'validity_seconds': 300,
            'img_link': 1
        }
        response = self.client.post(url_link, data_link, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, msg=response.data)


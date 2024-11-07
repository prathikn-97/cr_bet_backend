from rest_framework.test import APIClient, APITestCase
from django.contrib.auth import get_user_model
from rest_framework import status
from utils.helpers import get_user_info



class BaseTestCase(APITestCase):
    def setUp(self):
        user = get_user_info()
        token = f"Bearer {user['token']}"
        self.client.credentials(HTTP_AUTHORIZATION=token)
        self.client.defaults['companyId'] = user['companyId']
        self.client.defaults['userId'] = user['userId']
        self.client.defaults['type'] = 'virtueleBilling'
        super().setUp()

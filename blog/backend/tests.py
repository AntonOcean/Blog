import base64
import json

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

from backend.models import User, Question


class BaseViewTest(APITestCase):
    client = APIClient()

    def login_client(self, username="", password=""):
        url = reverse(
            "login",
        )

        response = self.client.post(
            url,
            data=json.dumps({
                "username": username,
                "password": password
            }),
            content_type="application/json"
        )

        self.token = response.data['token']

        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.token
        )

        return self.token

    def setUp(self):
        self.user_admin = User.objects.create_superuser("test_admin", None, "1234412")
        self.password = "1234412"
        self.username = "test_admin"


class TestTokenAuth(BaseViewTest):

    def test_token_auth(self):
        # Тест аутентификации через токены
        # Создаем суперюзера, получаем на него токен, пробуем доступ к users/ --header token

        token = self.login_client(self.username, self.password)
        print(token)
        response = self.client.get(reverse('user-list'))
        print(response.data)
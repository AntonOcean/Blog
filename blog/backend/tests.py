"""
Тест базового функционала, доступного на фронте
"""
import json

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from backend.models import User, Question


class BaseViewTest(APITestCase):
    client = APIClient()

    def logout_client(self):
        url = reverse("logout")
        response = self.client.post(
            url,
            {},
            content_type="application/json"
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=''
        )
        return response

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

        self.assertEqual(username, response.data['user']['username'])

        self.token = response.data['token']

        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.token
        )

        return self.token

    def setUp(self):
        self.user_admin = User.objects.create_superuser("test_admin", None, "1234412")
        self.admin_password = "1234412"
        self.admin_username = "test_admin"
        self.alice = User.objects.create_user("alice", None, "1234412f")
        self.alice_password = "1234412f"
        self.alice_username = "alice"
        self.bob = User.objects.create_user("bob", None, "1234412fl")
        self.bob_password = "1234412fl"
        self.bob_username = "bob"
        self.question = Question.objects.create(title="How to", long_text="opa", author_id=self.alice.id)


class TestTokenAuth(BaseViewTest):
    def test_token_auth_admin(self):
        """
        Тест аутентификации через токены
        Входим под суперюзера, получаем на него токен, пробуем доступ к users/ AdminOnly
        """
        token = self.login_client(self.admin_username, self.admin_password)
        response = self.client.get(reverse('user-list'))
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.logout_client()
        response = self.client.get(reverse('user-list'))
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

        token = self.login_client(self.admin_username, self.admin_password)
        response = self.client.get(reverse('user-list'))
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_token_auth_user(self):
        """
        Тест аутентификации через токены
        Входим под пользователя, получаем на него токен, пробуем доступ к users/ AdminOnly
        """
        token = self.login_client(self.alice_username, self.alice_password)
        response = self.client.get(reverse('user-list'))
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

        self.logout_client()
        response = self.client.get(reverse('user-list'))
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

        token = self.login_client(self.alice_username, self.alice_password)
        response = self.client.get(reverse('user-list'))
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)


class TestRegisteer(BaseViewTest):
    def test_register(self):
        """
        Зарегистрироваться может любой
        """
        url = reverse('register')

        response = self.client.post(
            url,
            data=json.dumps({
                "username": 'test_regiser',
                "password": '213423432'
            }),
            content_type="application/json"
        )

        self.assertEqual('test_regiser', response.data['user']['username'])
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)


class TestQuestion(BaseViewTest):
    def create_question(self):
        url = reverse('question-list')

        response = self.client.post(
            url,
            data=json.dumps({
                "title": 'test_question',
                "long_text": 'how to?'
            }),
            content_type="application/json"
        )
        return response

    def test_question_create(self):
        """
        Создавать вопрос могут только авторизованные пользователи
        При создании автоматически проставляется автор
        Неавторизованные - только чтение
        """
        response = self.create_question()
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

        url = reverse('question-list')
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        token = self.login_client(self.alice_username, self.alice_password)
        response = self.create_question()
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(response.data['author'], self.alice_username)

    def test_question_set_like(self):
        """
        Ставить лайки могут только авторизованные пользователи
        +1 вопрос; +1 автору
        Повторный лайк отменяет лайк
        """
        token = self.login_client(self.bob_username, self.bob_password)
        url = reverse("question-set-like", kwargs={'pk': self.question.pk})
        response = self.client.post(
            url,
            {},
            content_type="application/json"
        )
        self.assertEqual(1, response.data['question']['rating'])
        self.assertEqual(self.question.author.username, response.data['question']['author'])
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

        self.logout_client()
        token = self.login_client(self.admin_username, self.admin_password)
        # заходим под админа и проверяем рейтинг автора
        url = reverse(
            "user-profiles-detail",
            kwargs={
                'pk': self.question.author.pk,
                'user_pk': self.question.author.pk
            })
        response = self.client.get(
            url,
            {},
            content_type="application/json"
        )
        self.assertEqual(1, response.data['rating'])
        self.logout_client()

        token = self.login_client(self.bob_username, self.bob_password)
        url = reverse("question-set-like", kwargs={'pk': self.question.pk})
        response = self.client.post(
            url,
            {},
            content_type="application/json"
        )
        self.assertEqual(0, response.data['question']['rating'])
        self.assertEqual(self.question.author.username, response.data['question']['author'])
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

        self.logout_client()
        token = self.login_client(self.admin_username, self.admin_password)
        # заходим под админа и проверяем рейтинг автора
        url = reverse(
            "user-profiles-detail",
            kwargs={
                'pk': self.question.author.pk,
                'user_pk': self.question.author.pk
            })
        response = self.client.get(
            url,
            {},
            content_type="application/json"
        )
        self.assertEqual(0, response.data['rating'])

    def test_question_answer(self):
        """
        Отвечать на вопрос могут только авторизованные пользователи
        Неавторизованные - только чтение
        """
        url = reverse("question-answers-list", kwargs={'question_pk': self.question.pk})
        response = self.client.post(
            url,
            data=json.dumps({
                "text": 'ok, bro',
            }),
            content_type="application/json"
        )
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
        response = self.client.get(
            url,
            {},
            content_type="application/json"
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        token = self.login_client(self.bob_username, self.bob_password)
        response = self.client.post(
            url,
            data=json.dumps({
                "text": 'ok, bro',
            }),
            content_type="application/json"
        )
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(self.bob_username, response.data['author'])
        self.assertEqual(self.question.pk, int(response.data['question'].split('/')[-2]))


class TestAnswer(BaseViewTest):
    def test_answer_create(self):
        """
        Создавать ответ могут только авторизованные пользователи
        При создании автоматически проставляется автор
        Неавторизованные - только чтение
        """
        pass

    def test_answer_set_like(self):
        """
        Ставить лайки могут только авторизованные пользователи
        +1 ответ; +1 автору
        Повторный лайк отменяет лайк
        """
        pass

    def test_answer_right(self):
        """
        Помечать ответ верным может только автор вопроса
        """
        pass


class TestTag(BaseViewTest):
    def test_tag_create(self):
        """
        Тег создается при создании вопроса
        Использование тега +1 к рейтингу тега
        """
        pass


class TestProfile(BaseViewTest):
    def test_profile(self):
        """
        Посмотреть свой профиль может только владелец или админ
        """
        pass
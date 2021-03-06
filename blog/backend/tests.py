"""
Тест базового функционала, доступного на фронте before 572 after
"""
import json

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from backend.models import User, Question, Answer


class BaseViewTest(APITestCase):
    client = APIClient(enforce_csrf_checks=True)

    def logout_client(self):
        url = reverse("logout")
        response = self.client.post(url)
        self.client.credentials()
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
        self.answer = Answer.objects.create(question_id=self.question.id, text="how are you", author_id=self.bob.id)


class TestRegisteer(BaseViewTest):
    def register(self, data):
        url = reverse('register')
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type="application/json"
        )
        return response

    def test_register(self):
        """
        Зарегистрироваться может любой
        """
        data = {
                "username": 'test_regiser',
                "password": '213423432'
        }

        response = self.register(data)
        self.assertEqual('test_regiser', response.data['user']['username'])
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    def test_hack_rating(self):
        """
        Рейтинг при регистрации 0
        """
        data = {
                "username": 'test_register',
                "password": '213423432',
                "rating": 5,
        }
        response = self.register(data)
        self.assertEqual('test_register', response.data['user']['username'])
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

        test_register = User.objects.get(username='test_register')
        self.assertEqual(0, test_register.rating)


class TestQuestion(BaseViewTest):
    def create_question_answer(self):
        url = reverse("question-answers-list", kwargs={'question_pk': self.question.pk})
        response = self.client.post(
            url,
            data=json.dumps({
                "text": 'ok, bro',
            }),
            content_type="application/json"
        )
        return response

    def create_question(self, data):
        url = reverse('question-list')
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type="application/json"
        )
        return response

    def set_like(self):
        url = reverse("question-set-like", kwargs={'pk': self.question.pk})
        response = self.client.put(url)
        return response

    def test_question_create(self):
        """
        Создавать вопрос могут только авторизованные пользователи
        При создании автоматически проставляется автор
        Неавторизованные - только чтение
        """
        data = {
                "title": 'test_question',
                "long_text": 'how to?'
        }
        response = self.create_question(data)
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

        url = reverse('question-list')
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.login_client(self.alice_username, self.alice_password)
        response = self.create_question(data)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(response.data['author'], self.alice_username)

    def test_hack_rating(self):
        self.login_client(self.alice_username, self.alice_password)
        data = {
                "title": 'test_question',
                "long_text": 'how to?',
                "rating": 5,
        }
        response = self.create_question(data)
        self.assertEqual(0, response.data['rating'])

    def test_question_set_like(self):
        """
        Ставить лайки могут только авторизованные пользователи
        +1 вопрос; +1 автору
        Повторный лайк отменяет лайк
        """
        self.login_client(self.bob_username, self.bob_password)
        response = self.set_like()
        self.assertEqual(1, response.data['rating'])
        self.assertEqual(self.question.author.username, response.data['author'])
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        author = User.objects.get(id=self.question.author.pk)
        self.assertEqual(1, author.rating)
        response = self.set_like()
        self.assertEqual(0, response.data['rating'])
        self.assertEqual(self.question.author.username, response.data['author'])
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        author = User.objects.get(id=self.question.author.pk)
        self.assertEqual(0, author.rating)

    def test_question_answer(self):
        """
        Отвечать на вопрос могут только авторизованные пользователи
        Неавторизованные - только чтение
        """
        url = reverse("question-answers-list", kwargs={'question_pk': self.question.pk})
        response = self.create_question_answer()
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.login_client(self.bob_username, self.bob_password)
        response = self.create_question_answer()
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(self.bob_username, response.data['author'])
        self.assertEqual(self.question.pk, int(response.data['question'].split('/')[-2]))

    def test_sort(self):
        url = reverse('question-list')
        response = self.client.get(
            url,
            data={"sort": "rating"},
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)


class TestAnswer(BaseViewTest):
    def create_answer(self):
        url = reverse('question-answers-list', kwargs={'question_pk': self.question.pk})
        response = self.client.post(
            url,
            data=json.dumps({
                "text": 'test answer',
            }),
            content_type="application/json"
        )
        return response

    def get_question_detail(self):
        url = reverse('question-detail', kwargs={'pk': self.question.pk})
        response = self.client.get(url)
        return response

    def test_answer_create(self):
        """
        Создавать ответ могут только авторизованные пользователи
        При создании автоматически проставляется автор
        Неавторизованные - только чтение
        """
        response = self.create_answer()
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
        url = reverse('question-answers-list', kwargs={'question_pk': self.question.pk})
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        response = self.get_question_detail()
        self.assertEqual(response.data['count_answers'], 1)
        self.login_client(self.bob_username, self.bob_password)
        response = self.create_answer()
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(self.bob_username, response.data['author'])
        response = self.get_question_detail()
        self.assertEqual(response.data['count_answers'], 2)

    def test_answer_set_like(self):
        """
        Ставить лайки могут только авторизованные пользователи
        +1 ответ; +1 автору
        Повторный лайк отменяет лайк
        """
        self.login_client(self.bob_username, self.bob_password)
        url = reverse("answer-set-like", kwargs={'pk': self.answer.pk})
        response = self.client.put(url)
        self.assertEqual(1, response.data['rating'])
        self.assertEqual(self.answer.author.username, response.data['author'])
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        author = User.objects.get(id=self.answer.author.pk)
        self.assertEqual(1, author.rating)
        url = reverse("answer-set-like", kwargs={'pk': self.answer.pk})
        response = self.client.put(url)
        self.assertEqual(0, response.data['rating'])
        self.assertEqual(self.answer.author.username, response.data['author'])
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        author = User.objects.get(id=self.answer.author.pk)
        self.assertEqual(0, author.rating)

    def test_answer_right(self):
        """
        Помечать ответ верным может только автор вопроса
        Повторная метка отменяет метку
        """
        author = self.question.author
        self.assertEqual(author.username, self.alice_username)  # alice - question author

        self.login_client(self.bob_username, self.bob_password)

        url = reverse("answer-mark-as-right", kwargs={
            'pk': self.answer.id,
        })
        response = self.client.put(url)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.logout_client()

        self.login_client(self.alice_username, self.alice_password)
        response = self.client.put(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(True, response.data['right_answer'])
        response = self.client.put(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(False, response.data['right_answer'])


class TestTag(BaseViewTest):
    def create_question_tags(self, data):
        url = reverse('question-list')
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type="application/json"
        )
        return response

    def test_sort(self):
        url = reverse('tag-list')
        response = self.client.get(
            url,
            data={"sort": "rating", "limit": "10"},
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_tag_create(self):
        """
        Тег создается при создании вопроса
        Использование тега +1 к рейтингу тега
        """
        self.login_client(self.alice_username, self.alice_password)
        data = {
                "title": 'test_question',
                "long_text": 'how to?',
                "tags": ["test_tag_1", "test_tag_2"]
        }
        response = self.create_question_tags(data)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(['test_tag_1', 'test_tag_2'], response.data['tags'])
        url = reverse('tag-list')
        response = self.client.get(url)
        self.assertEqual(2, len(response.data['results']))
        self.assertEqual(1, response.data['results'][0]['rating'])
        data = {
                "title": 'test_question_1',
                "long_text": 'how to?',
                "tags": ["test_tag_1", "test_tag_2"]
        }
        response = self.create_question_tags(data)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(['test_tag_1', 'test_tag_2'], response.data['tags'])
        url = reverse('tag-list')
        response = self.client.get(url)
        self.assertEqual(2, len(response.data['results']))
        self.assertEqual(2, response.data['results'][0]['rating'])


class TestProfile(BaseViewTest):
    def change_profile(self, data, url):
        response = self.client.put(
            url,
            data=json.dumps(data),
            content_type="application/json"
        )
        return response

    def test_sort(self):
        url = reverse('user-list')
        response = self.client.get(
            url,
            data={"sort": "rating", "limit": "10"},
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_profile(self):
        """
        Посмотреть свой профиль может только владелец или админ
        """
        self.login_client(self.admin_username, self.admin_password)
        # заходим под админа и смотрим пользователя
        url = reverse(
            "user-profile",
            kwargs={
                'pk': self.answer.author.pk,
            })
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(self.bob_username, response.data['username'])
        self.logout_client()

        self.login_client(self.alice_username, self.alice_password)
        response = self.client.get(url)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.logout_client()

        self.login_client(self.bob_username, self.bob_password)
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(self.bob_username, response.data['username'])

    def test_change(self):
        """
        Поле рейтинг не изменно со стороны пользователя
        """
        self.login_client(self.bob_username, self.bob_password)
        url = reverse(
            "user-profile",
            kwargs={
                'pk': self.answer.author.pk,
            })
        data = {
                "rating": 5,
                "username": "dde"
        }
        response = self.change_profile(data, url)
        self.assertEqual("dde", response.data['username'])
        self.assertEqual(0, response.data['rating'])
        data = {
                "rating": 5,
                "username": "alice"
        }
        response = self.change_profile(data, url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
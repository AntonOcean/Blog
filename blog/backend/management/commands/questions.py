import random

from django.core.management import BaseCommand
from faker import Faker

from backend.models import Question, User

USER_COUNT = 10000
QUESTION_COUNT = 100000


class Command(BaseCommand):
    def handle(self, *args, **options):
        # self.create_users()
        users = User.objects.all()

        self.create_questions(users=users)
        questions = Question.objects.all()

    def create_users(self):
        users = []
        faker = Faker()
        for i in range(USER_COUNT):
            user = User(username=faker.user_name()+str(i), password='passwd{}'.format(i), email=faker.email())
            users.append(user)

        User.objects.bulk_create(users, batch_size=100)

    def create_questions(self, users, tags=None):
        questions = []
        faker = Faker()
        for _ in range(QUESTION_COUNT):
            question = Question(
                title=faker.sentence()[:random.randint(20, 100)],
                long_text=faker.text(),
                author=random.choice(users),
            )
            questions.append(question)

        Question.objects.bulk_create(questions, batch_size=100)
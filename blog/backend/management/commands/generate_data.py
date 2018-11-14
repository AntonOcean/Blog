from django.core.management.base import  BaseCommand
from datetime import datetime
from faker import Faker
import random
from backend.models import Question, Tag, Like, User, Answer
from types import FunctionType
from functools import wraps

USER_COUNT = 10000
TAG_COUNT = 10000
QUESTION_COUNT = 100000
ANSWER_COUNT = 1000000
VOTE_COUNT = 2000000


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.create_users()
        users = User.objects.all()

        self.create_tags()
        tags = Tag.objects.all()

        self.create_questions(users=users, tags=tags)
        questions = Question.objects.all()

        self.create_answers(users=users, questions=questions)
        answers = Answer.objects.all()

        self.create_likes(users=users, answers=answers, questions=questions)

    def create_users(self):
        users = []
        faker = Faker()
        for i in range(USER_COUNT):
            user = User(username=faker.user_name()+str(i), password='passwd{}'.format(i), email=faker.email())
            users.append(user)

        User.objects.bulk_create(users, batch_size=10000)

    def create_tags(self):
        tags = []
        faker = Faker()
        for i in range(TAG_COUNT):
            tag = Tag(name=faker.word()+str(i))
            tags.append(tag)

        Tag.objects.bulk_create(tags, batch_size=10000)



    def create_answers(self, users, questions):
        answers = []
        faker = Faker()
        for _ in range(ANSWER_COUNT):
            answer = Answer(author=random.choice(users), question=random.choice(questions), text=faker.text())
            answers.append(answer)

        Answer.objects.bulk_create(answers, batch_size=10000)

    def count_answer_count(self, questions):
        for question in questions:
            question.answer_count = question.answer_set.count()
        Question.bulk_objects.bulk_update(questions, update_fields=['answer_count'], batch_size=10000)


    def generate_likes_fast(self, users):
        # Генерация за 41ю6 минут!!!
        Like.objects.all().delete()

        questions = Question.objects.filter(pk__lte=10000)
        answers = Answer.objects.filter(pk__lte=10000)

        i = 1

        while(Like.objects.all().count() < 2000000):
            user = users[i]
            i += 1
            list_of_likes = []

            _questions = questions.exclude(author=user)
            for question in _questions:
                value = random.choice([1, -1])
                like = Like.set_like(user=user, obj=question)
                list_of_likes.append(like)

            _answers = answers.exclude(author=user)
            for answer in _answers:
                value = random.choice([1, -1])
                like = LikeDislike(vote=value, user=user, content_object=answer)
                list_of_likes.append(like)

            LikeDislike.objects.bulk_create(list_of_likes)
            for like in list_of_likes:
                like.content_object.rate += like.vote
                like.content_object.save(update_fields=['rate'])

    # def add_tag_question_relations(self, questions, tags):
    #     for question in questions:
    #         tags_for_questions = []
    #         for _ in range(random.randint(1, 5)):
    #             tag = random.choice(tags)
    #             if tag.pk not in tags_for_questions:
    #                 tags_for_questions.append(tag.pk)
    #         question.tags.add(*tags_for_questions)
    #
    #     Question.bulk_objects.bulk_update(questions, update_fields=['tags'], batch_size=10000)

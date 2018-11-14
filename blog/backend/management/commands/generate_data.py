from django.core.management.base import BaseCommand
from django_bulk_update.helper import bulk_update
from faker import Faker
import random
from backend.models import Question, Tag, Like, User, Answer


USER_COUNT = 10000
TAG_COUNT = 10000
QUESTION_COUNT = 100000
ANSWER_COUNT = 1000000
LIKE_COUNT = 2000000


class Command(BaseCommand):
    faker = Faker()

    def handle(self, *args, **options):
        self.create_users()
        users = User.objects.all()
        print("Шаг 1 из 8 Пользователи созданы")

        self.create_tags()
        tags = Tag.objects.all()
        print("Шаг 2 из 8 Теги созданы")

        self.create_questions(users=users)
        questions = Question.objects.all()
        print("Шаг 3 из 8 Вопросы созданы")

        self.add_tag_question_relations(questions=questions, tags=tags)
        print("Шаг 4 из 8 Добавлены теги")

        self.create_answers(users=users, questions=questions)
        answers = Answer.objects.all()
        print("Шаг 5 из 8 Ответы созданы")

        self.update_answer_count(questions=questions)
        print("Шаг 6 из 8 Обновлен счетчик ответов у вопросов")

        self.update_tag_rating(tags)
        print("Шаг 7 из 8 Обновлен рейтинг тегов")

        self.create_likes(users=users, answers=answers, questions=questions)
        print("Шаг 8 из 8 Лайки созданы")

    def create_users(self):
        users = []
        for i in range(USER_COUNT):
            user = User(username=self.faker.user_name()+str(i), password='passwd{}'.format(i), email=self.faker.email())
            users.append(user)
        User.objects.bulk_create(users, batch_size=100)

    def create_tags(self):
        tags = []
        for i in range(TAG_COUNT):
            tag = Tag(name=self.faker.word()+str(i))
            tags.append(tag)
        Tag.objects.bulk_create(tags, batch_size=100)

    def create_questions(self, users):
        questions = []
        for _ in range(QUESTION_COUNT):
            author = random.choice(users)
            question = Question(
                title=self.faker.sentence()[:random.randint(20, 100)],
                long_text=self.faker.text(),
                author_id=author.id,
            )
            questions.append(question)
        Question.objects.bulk_create(questions, batch_size=100)

    def add_tag_question_relations(self, questions, tags):
        for question in questions:
            tag_list = [random.choice(tags) for _ in range(random.randint(1, 6))]
            tag_id_list = []
            for tag in tag_list:
                if tag.pk not in tag_id_list:
                    tag_id_list.append(tag.pk)
            question.tags.add(*tag_id_list)
        bulk_update(questions, batch_size=100)

    def create_answers(self, users, questions):
        answers = []
        for _ in range(ANSWER_COUNT):
            answer = Answer(author=random.choice(users), question=random.choice(questions), text=self.faker.text())
            answers.append(answer)
        Answer.objects.bulk_create(answers, batch_size=100)

    def update_answer_count(self, questions):
        for question in questions:
            question.count_answers = question.answers.count()
        bulk_update(questions, update_fields=['count_answers'], batch_size=100)

    def update_tag_rating(self, tags):
        for tag in tags:
            tag.rating = tag.questions.count()
        bulk_update(tags, update_fields=['rating'], batch_size=100)

    def create_likes(self, users, answers, questions):
        big_data = list(answers) + list(questions)
        author_list = []
        answer_list = []
        question_list = []
        for _ in range(LIKE_COUNT):
            obj = random.choice(big_data)
            obj_author = obj.author
            like_add = Like.set_like(obj=obj, user=random.choice(users))
            if like_add:
                obj.rating += 1
                obj_author.rating += 1
            else:
                obj.rating -= 1
                obj_author.rating -= 1
            if obj._meta.model == Question:
                question_list.append(obj)
            else:
                answer_list.append(obj)
            author_list.append(obj_author)
        bulk_update(question_list, update_fields=['rating'], batch_size=100)
        bulk_update(answer_list, update_fields=['rating'], batch_size=100)
        bulk_update(author_list, update_fields=['rating'], batch_size=100)

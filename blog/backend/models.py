from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import F


class UserCustomManager(UserManager):
    def top_users(self, key='rating', limit=10):
        return self.order_by(f'-{key}')[:limit]


class User(AbstractUser):
    avatar = models.ImageField(upload_to='media/%Y/%m/%d/', null=True, max_length=255, verbose_name='Аватарка')
    rating = models.IntegerField(default=0, auto_created=True, verbose_name='Рейтинг')
    objects = UserCustomManager()

    def rating_up(self):
        User.objects.filter(id=self.id).update(rating=F('rating') + 1)

    def rating_down(self):
        User.objects.filter(id=self.id).update(rating=F('rating') - 1)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class TagManager(models.Manager):
    def top_tags(self, key='rating', limit=10):
        return self.order_by(f'-{key}')[:limit]


class Tag(models.Model):
    name = models.CharField(max_length=20, unique=True, verbose_name='Название')
    rating = models.IntegerField(default=0, auto_created=True, verbose_name='Рейтинг')
    objects = TagManager()

    def rating_up(self):
        Tag.objects.filter(id=self.id).update(rating=F('rating') + 1)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Like(models.Model):
    user = models.ForeignKey(User, related_name='likes', on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    @staticmethod
    def set_like(obj, user):
        obj_type = ContentType.objects.get_for_model(obj)
        like, is_created = Like.objects.get_or_create(
            content_type=obj_type, object_id=obj.id, user=user)
        if is_created:
            obj.author.rating_up()
            obj.rating_up()
        else:
            obj.author.rating_down()
            obj.rating_down()
            like.delete()
        return like


class QuestionManager(models.Manager):
    def hot_questions(self):
        return self.order_by('-rating')


class Question(models.Model):
    title = models.CharField(max_length=50, verbose_name='Название')
    long_text = models.TextField(verbose_name='Текст')
    author = models.OneToOneField(User, on_delete=models.CASCADE, related_name='question', verbose_name='Автор')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    tags = models.ManyToManyField(Tag, verbose_name='Теги', related_name='questions')
    rating = models.IntegerField(default=0, auto_created=True, verbose_name='Рейтинг')
    count_answers = models.PositiveIntegerField(default=0, auto_created=True, verbose_name='Количество ответов')
    likes = GenericRelation(Like, related_name='likes')
    objects = QuestionManager()

    @property
    def short_text(self):
        current_text = self.long_text
        if len(current_text) <= 100:
            return current_text
        return self.long_text[:100] + '...'

    def rating_up(self):
        Question.objects.filter(id=self.id).update(rating=F('rating') + 1)

    def rating_down(self):
        Question.objects.filter(id=self.id).update(rating=F('rating') - 1)

    def count_up(self):
        Question.objects.filter(id=self.id).update(rating=F('count_answers') + 1)

    def add_tag(self, name):
        tag, is_created = Tag.objects.get_or_create(name=name)
        self.tags.add(tag)
        if not is_created:
            tag.rating_up()
        return tag

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        ordering = ['-created']


class AnswerManager(models.Manager):
    def create(self, *args, **kwargs):
        obj = super().create(*args, **kwargs)
        obj.question.count_up()


class Answer(models.Model):
    text = models.TextField(verbose_name='Текст')
    author = models.OneToOneField(User, on_delete=models.CASCADE, related_name='answer', verbose_name='Автор')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    right_answer = models.BooleanField(default=False, verbose_name='Верный ответ')
    question = models.ForeignKey(Question, blank=True, null=True, related_name='answers', verbose_name='Вопрос', on_delete=models.CASCADE)
    rating = models.IntegerField(default=0, auto_created=True, verbose_name='Рейтинг')
    likes = GenericRelation(Like, related_name='likes')
    objects = AnswerManager()

    def rating_up(self):
        Answer.objects.filter(id=self.id).update(rating=F('rating') + 1)

    def rating_down(self):
        Answer.objects.filter(id=self.id).update(rating=F('rating') - 1)

    def mark_as_right(self):
        Answer.objects.filter(id=self.id).update(right_answer=True)

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'
        ordering = ['-rating', 'created']
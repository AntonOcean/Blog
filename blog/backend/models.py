from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import F


class UserManager(models.Manager):
    def top_ten_users(self):
        return self.order_by('-rating')[:10]


class User(AbstractUser):
    avatar = models.ImageField(verbose_name='Аватарка')
    rating = models.IntegerField(default=0, verbose_name='Рейтинг')

    def rating_up(self):
        User.objects.filter(id=self.id).update(rating=F('rating') + 1)

    def rating_down(self):
        User.objects.filter(id=self.id).update(rating=F('rating') - 1)


class TagManager(models.Manager):
    def top_ten_tags(self):
        return self.order_by('-rating')[:10]


class Tag(models.Model):
    name = models.CharField(max_length=20, unique=True, verbose_name='Название')
    rating = models.IntegerField(default=0, verbose_name='Рейтинг')

    def rating_up(self):
        Tag.objects.filter(id=self.id).update(rating=F('rating') + 1)

    class Meta:
        verbose_name = 'Теги'


class Like(models.Model):
    user = models.ForeignKey(User, related_name='likes', on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')


class Answer(models.Model):
    text = models.TextField(verbose_name='Текст')
    author = models.OneToOneField(User, on_delete=models.CASCADE, related_name='answer', verbose_name='Автор')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    right_answer = models.BooleanField(default=False, verbose_name='Верный ответ')
    rating = models.IntegerField(default=0, verbose_name='Рейтинг')
    likes = GenericRelation(Like)

    def set_like(self, user):
        obj_type = ContentType.objects.get_for_model(Answer)
        like, is_created = Like.objects.get_or_create(
            content_type=obj_type, object_id=self.id, user=user)
        if is_created:
            self.author.rating_up()
            self.rating_up()
        else:
            self.author.rating_down()
            self.rating_down()
            like.delete()

    def rating_up(self):
        Answer.objects.filter(id=self.id).update(rating=F('rating') + 1)

    def rating_down(self):
        Answer.objects.filter(id=self.id).update(rating=F('rating') - 1)

    def mark_as_right(self):
        Answer.objects.filter(id=self.id).update(right_answer=True)

    class Meta:
        verbose_name = 'Ответы'
        ordering = ['-rating', 'created']


class QuestionManager(models.Manager):
    def hot_questions(self):
        return self.order_by('-rating')


class Question(models.Model):
    title = models.CharField(max_length=50, verbose_name='Название')
    text = models.TextField()
    author = models.OneToOneField(User, on_delete=models.CASCADE, related_name='question', verbose_name='Автор')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    tags = models.ManyToManyField(Tag, verbose_name='Теги')
    rating = models.IntegerField(default=0, verbose_name='Рейтинг')
    answers = models.ForeignKey(Answer, blank=True, null=True, verbose_name='Ответы', on_delete=models.CASCADE)
    likes = GenericRelation(Like)
    object = QuestionManager()

    def set_like(self, user):
        obj_type = ContentType.objects.get_for_model(Question)
        like, is_created = Like.objects.get_or_create(
            content_type=obj_type, object_id=self.id, user=user)
        if is_created:
            self.author.rating_up()
            self.rating_up()
        else:
            self.author.rating_down()
            self.rating_down()
            like.delete()

    def rating_up(self):
        Question.objects.filter(id=self.id).update(rating=F('rating') + 1)

    def rating_down(self):
        Question.objects.filter(id=self.id).update(rating=F('rating') - 1)

    def add_tag(self, name):
        tag, is_created = Tag.objects.get_or_create(name=name)
        self.tags.add(tag)
        if not is_created:
            tag.rating_up()

    class Meta:
        verbose_name = 'Вопросы'
        ordering = ['-created']

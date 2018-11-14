from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import F
from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver

from backend.managers import BlogUserManager, TagManager, QuestionManager


class User(AbstractUser):
    avatar = models.ImageField(upload_to='media/%Y/%m/%d/', blank=True, null=True, max_length=255, verbose_name='Аватарка')
    rating = models.IntegerField(default=0, auto_created=True, verbose_name='Рейтинг')
    objects = BlogUserManager()

    def __str__(self):
        return self.username


class Tag(models.Model):
    name = models.CharField(max_length=20, unique=True, verbose_name='Название')
    rating = models.IntegerField(default=0, auto_created=True, verbose_name='Рейтинг')
    objects = TagManager()

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
        if not is_created:
            like.delete()


class Question(models.Model):
    title = models.CharField(max_length=50, verbose_name='Название')
    long_text = models.TextField(verbose_name='Текст')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions', verbose_name='Автор')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    tags = models.ManyToManyField(Tag, verbose_name='Теги', related_name='questions')
    rating = models.IntegerField(default=0, auto_created=True, verbose_name='Рейтинг')
    count_answers = models.PositiveIntegerField(default=0, auto_created=True, verbose_name='Количество ответов')
    likes = GenericRelation(Like, blank=True, null=True, related_name='likes')
    objects = QuestionManager()

    @property
    def short_text(self):
        current_text = self.long_text
        if len(current_text) <= 100:
            return current_text
        return self.long_text[:100] + '...'

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        ordering = ['-created']


class Answer(models.Model):
    text = models.TextField(verbose_name='Текст')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answers', verbose_name='Автор')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    right_answer = models.BooleanField(default=False, auto_created=True, verbose_name='Верный ответ')
    question = models.ForeignKey(Question, related_name='answers', verbose_name='Вопрос', on_delete=models.CASCADE)
    rating = models.IntegerField(default=0, auto_created=True, verbose_name='Рейтинг')
    likes = GenericRelation(Like, blank=True, null=True, related_name='likes')

    def mark_as_right(self):
        self.right_answer = not self.right_answer
        return self.right_answer

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'
        ordering = ['-rating', 'created']


@receiver(post_save, sender=Answer)
def up_answer_count(sender, instance, created, **kwargs):
    if created:
        instance.question.count_answers += 1
        instance.question.save()


@receiver(post_save, sender=Like)
def up_rating(sender, instance, created, **kwargs):
    obj = instance.content_object
    obj.rating += 1
    obj.author.rating += 1
    obj.author.save()
    obj.save()


@receiver(post_delete, sender=Like)
def down_rating(sender, instance, **kwargs):
    obj = instance.content_object
    obj.rating -= 1
    obj.author.rating -= 1
    obj.author.save()
    obj.save()


@receiver(m2m_changed, sender=Question.tags.through)
def up_tag_rating(sender, instance, model, pk_set, action, **kwargs):
    if action == "post_add":
        model.objects.filter(id__in=pk_set).update(rating=F('rating')+1)

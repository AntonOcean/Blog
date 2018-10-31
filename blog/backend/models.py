from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import F


class User(AbstractUser):
    avatar = models.ImageField(verbose_name='Аватарка')
    rating = models.IntegerField(default=0, verbose_name='Рейтинг')


class Tag(models.Model):
    name = models.CharField(max_length=20, unique=True, verbose_name='Название')

    class Meta:
        verbose_name = 'Теги'


class Answer(models.Model):
    text = models.TextField(verbose_name='Текст')
    author = models.OneToOneField(User, on_delete=models.CASCADE, related_name='answer', verbose_name='Автор')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    right_answer = models.BooleanField(default=False, verbose_name='Верный ответ')
    rating = models.IntegerField(default=0, verbose_name='Рейтинг')
    fans = models.ManyToManyField(User, related_name='answers')

    def rating_change(self, user):
        have_liked = self.fans.filter(id=user.id).exists()
        if have_liked:
            User.objects.filter(id=self.author_id).update(rating=F('rating') - 1)
            Answer.objects.filter(id=self.id).update(rating=F('rating') - 1)
            self.fans.remove(user)
        else:
            User.objects.filter(id=self.author_id).update(rating=F('rating') + 1)
            Answer.objects.filter(id=self.id).update(rating=F('rating') + 1)
            self.fans.add(user)


class Question(models.Model):
    title = models.CharField(max_length=50, verbose_name='Название')
    text = models.TextField()
    author = models.OneToOneField(User, on_delete=models.CASCADE, related_name='question', verbose_name='Автор')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    tags = models.ManyToManyField(Tag, verbose_name='Теги')
    rating = models.IntegerField(default=0, verbose_name='Рейтинг')
    answers = models.ForeignKey(Answer, blank=True, null=True, verbose_name='Ответы', on_delete=models.CASCADE)
    fans = models.ManyToManyField(User, related_name='questions')

    def rating_change(self, user):
        have_liked = self.fans.filter(id=user.id).exists()
        if have_liked:
            User.objects.filter(id=self.author_id).update(rating=F('rating') - 1)
            Question.objects.filter(id=self.id).update(rating=F('rating') - 1)
            self.fans.remove(user)
        else:
            User.objects.filter(id=self.author_id).update(rating=F('rating') + 1)
            Question.objects.filter(id=self.id).update(rating=F('rating') + 1)
            self.fans.add(user)

    class Meta:
        verbose_name = 'Вопросы'
        ordering = ['-created']

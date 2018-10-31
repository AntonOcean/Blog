from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.models import ContentType
from django.db import models


class User(AbstractUser):
    avatar = models.ImageField(verbose_name='Аватарка')
    rating = models.IntegerField(default=0, verbose_name='Рейтинг')


class Tag(models.Model):
    name = models.CharField(max_length=20, verbose_name='Название')

    class Meta:
        verbose_name = 'Теги'


class Answer(models.Model):
    text = models.TextField(verbose_name='Текст')
    author = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Автор')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    right_answer = models.BooleanField(default=False, verbose_name='Верный ответ')
    rating = models.IntegerField(default=0, verbose_name='Рейтинг')

    def rating_change(self, user):
        _, created = UserAnswer.objects.get_or_create(answer_id=self.id, author_id=user.id)
        if created:
            self.rating += 1
            self.author.rating += 1
        else:
            self.rating -= 1
            self.author.rating -= 1

    class Meta:
        verbose_name = 'Ответы'
        ordering = ['-rating', '-created']


class Question(models.Model):
    title = models.CharField(max_length=50, verbose_name='Название')
    text = models.TextField()
    author = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Автор')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    tags = models.ManyToManyField(Tag, verbose_name='Теги')
    rating = models.IntegerField(default=0, verbose_name='Рейтинг')
    answers = models.ForeignKey(Answer, blank=True, null=True, verbose_name='Ответы', on_delete=models.CASCADE)

    def rating_change(self, user):
        obj, created = UserQuestion.objects.get_or_create(question_id=self.id, author_id=user.id)
        if created:
            self.author.rating += 1
            self.rating += 1
        else:
            self.author.rating -= 1
            self.rating -= 1
            obj.delete()

    class Meta:
        verbose_name = 'Вопросы'
        ordering = ['-created']


class UserQuestion(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('author', 'question'),)


class UserAnswer(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('author', 'answer'),)
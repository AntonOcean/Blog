from django.contrib.auth.models import User, AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class ProfileManager(models.Manager):
    def top_users(self, key='rating', limit=10):
        return self.order_by(f'-{key}')[:limit]


class Profile(models.Model):
    user = models.OneToOneField(User, verbose_name='Профиль', related_name='profile', on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='media/%Y/%m/%d/', blank=True, null=True, max_length=255, verbose_name='Аватарка')
    rating = models.IntegerField(default=0, auto_created=True, verbose_name='Рейтинг')
    objects = ProfileManager()

    def rating_up(self):
        self.rating += 1

    def rating_down(self):
        self.rating -= 1

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профиль'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class TagManager(models.Manager):
    def top_tags(self, key='rating', limit=10):
        return self.order_by(f'-{key}')[:limit]


class Tag(models.Model):
    name = models.CharField(max_length=20, unique=True, verbose_name='Название')
    rating = models.IntegerField(default=0, auto_created=True, verbose_name='Рейтинг')
    objects = TagManager()

    def rating_up(self):
        self.rating += 1

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
            obj.author.profile.rating_up()
            obj.rating_up()
        else:
            obj.author.profile.rating_down()
            obj.rating_down()
            like.delete()
        return obj.rating


class QuestionManager(models.Manager):
    def hot_questions(self, sort_by='rating'):
        return self.order_by(f'-{sort_by}')


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

    def rating_up(self):
        self.rating += 1

    def rating_down(self):
        self.rating -= 1

    def count_up(self):
        self.count_answers += 1

    def add_tag(self, name):
        tag, is_created = Tag.objects.get_or_create(name=name)
        self.tags.add(tag)
        if not is_created:
            tag.rating_up()
            tag.save()
        return tag

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

    def rating_up(self):
        self.rating += 1

    def rating_down(self):
        self.rating -= 1

    def mark_as_right(self):
        self.right_answer = not self.right_answer
        return self.right_answer

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'
        ordering = ['-rating', 'created']
        default_manager_name = 'objects'
from django.contrib.auth.models import UserManager
from django.db import models


class BlogUserManager(UserManager):
    def top_users(self, key='rating', limit=10):
        return self.order_by(f'-{key}')[:limit]


class TagManager(models.Manager):
    def top_tags(self, key='rating', limit=10):
        return self.order_by(f'-{key}')[:limit]


class QuestionManager(models.Manager):
    def hot_questions(self, sort_by='rating'):
        return self.order_by(f'-{sort_by}')

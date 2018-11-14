from django.contrib.auth.models import UserManager
from django.db import models
from django.db.models import QuerySet


class BlogUserManager(UserManager):
    def top_users(self, key='rating', limit=10):
        return self.order_by(f'-{key}')[:limit]


class QuestionQuerySet(QuerySet):
    def hot_questions(self, sort_by='rating'):
        return self.order_by(f'-{sort_by}')


class TagQuerySet(QuerySet):
    def top_tags(self, key='rating', limit=10):
        return self.order_by(f'-{key}')[:limit]


TagManager = models.Manager.from_queryset(TagQuerySet)
QuestionManager = models.Manager.from_queryset(QuestionQuerySet)
from django.contrib import admin

from backend.models import Question, User, Tag, Answer

admin.site.register((Question, User, Tag, Answer))
from django.contrib import admin

from backend.models import Question, Tag, Answer, Profile

admin.site.register((Question, Profile, Tag, Answer))
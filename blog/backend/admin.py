from django.contrib import admin

from backend.models import Question, Tag, Answer, Profile


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('created', 'author', 'rating', 'question')
    readonly_fields = ('created', 'rating')


class AnswerInline(admin.TabularInline):
    model = Answer


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created', 'rating')
    readonly_fields = ('created', 'rating', 'count_answers')
    list_filter = ('tags', 'author')

    inlines = [AnswerInline]


class QuestionInline(admin.TabularInline):
    model = Question.tags.through


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', )
    readonly_fields = ('rating', )
#     add fields


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'rating')
    readonly_fields = ('rating',)

    inlines = [QuestionInline]
    exclude = ('tags',)

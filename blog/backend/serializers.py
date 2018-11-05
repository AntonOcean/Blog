from rest_framework import serializers
from django.contrib.auth.models import User

from backend.models import Tag, Question, Answer, Profile


class QuestionSerializer(serializers.HyperlinkedModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    rating = serializers.IntegerField(read_only=True)
    count_answers = serializers.IntegerField(read_only=True)
    answers = serializers.HyperlinkedIdentityField(
        many=True,
        view_name='question-answers-list',
        lookup_url_kwarg='question_pk',
        read_only=True
    )
    tags = serializers.SlugRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        slug_field='name'
     )

    class Meta:
        model = Question
        fields = ('url', 'title', 'long_text', 'author', 'rating', 'answers', 'tags', 'short_text', 'count_answers')


class UserSerializer(serializers.HyperlinkedModelSerializer):
    avatar = serializers.ImageField(source='profile.avatar')
    profile = serializers.HyperlinkedIdentityField(
        view_name='user-profile-list',
        lookup_url_kwarg='user_pk',
        read_only=True
    )

    class Meta:
        model = User
        fields = ('url', 'username', 'profile', 'email', 'password', 'avatar')


class TagSerializer(serializers.HyperlinkedModelSerializer):
    questions = serializers.HyperlinkedIdentityField(
        many=True,
        view_name='tag-questions-list',
        lookup_url_kwarg='tag_pk',
        read_only=True
    )
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Tag
        fields = ('url', 'name', 'rating', 'questions')


class AnswerSerializer(serializers.HyperlinkedModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    rating = serializers.IntegerField(read_only=True)
    right_answer = serializers.BooleanField(read_only=True)
    question = serializers.HyperlinkedRelatedField(
        read_only=True,
        view_name='question-detail',
    )

    class Meta:
        model = Answer
        fields = ('url', 'text', 'author', 'created', 'right_answer', 'rating', 'question')


class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    # user = models.OneToOneField(User, verbose_name='Профиль', related_name='profile', on_delete=models.CASCADE)
    # avatar = models.ImageField(upload_to='media/%Y/%m/%d/', blank=True, null=True, max_length=255, verbose_name='Аватарка')
    # rating = models.IntegerField(default=0, auto_created=True, verbose_name='Рейтинг')
    rating = serializers.IntegerField(read_only=True)
    username = serializers.CharField(source='user.username')
    email = serializers.EmailField(source='user.email')
    user = serializers.HyperlinkedRelatedField(
        read_only=True,
        view_name='user-detail',
    )

    class Meta:
        model = Profile
        fields = ('url', 'avatar', 'rating', 'user', 'username', 'email')
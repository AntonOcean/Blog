from django.contrib.auth import authenticate
from rest_framework import serializers

from backend.models import Tag, Question, Answer, User


class CreateUserSerializer(serializers.ModelSerializer):
    """
    Регистрация
    """
    avatar = serializers.ImageField(required=False)

    def create(self, validated_data):
        user = User.objects.create_user(validated_data['username'],
                                        validated_data.get('email'),
                                        validated_data['password'])
        return user

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'avatar')
        extra_kwargs = {'password': {'write_only': True,}}


class LoginUserSerializer(serializers.Serializer): # DEBUG feature
    username = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Неверные логин или пароль.")


class QuestionSerializer(serializers.HyperlinkedModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    rating = serializers.IntegerField(read_only=True)
    count_answers = serializers.IntegerField(read_only=True)
    answers = serializers.HyperlinkedIdentityField(
        view_name='question-answers-list',
        lookup_url_kwarg='question_pk',
        read_only=True
    )
    tags = serializers.SlugRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        slug_field='name',
        required=False,
     )

    class Meta:
        model = Question
        fields = ('url', 'title', 'long_text', 'author', 'rating', 'answers', 'tags', 'short_text', 'count_answers')


class UserSerializer(serializers.HyperlinkedModelSerializer):
    """
    Лист пользователей
    """

    class Meta:
        model = User
        fields = ('username', 'rating')


class TagSerializer(serializers.HyperlinkedModelSerializer):
    """
    Вопросы по тегу, лист тегов
    """
    questions = serializers.HyperlinkedIdentityField(
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
    """
    Профиль пользователя
    """
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = ('avatar', 'rating', 'username', 'email')
from django.contrib.auth import authenticate
from rest_framework import serializers, validators
from django.contrib.auth.models import User
from rest_framework_nested.relations import NestedHyperlinkedRelatedField
# from knox.serializers import UserSerializer

from backend.models import Tag, Question, Answer, Profile


class CreateUserSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(source='profile.avatar', required=False)
    profile = NestedHyperlinkedRelatedField(
        read_only=True,
        view_name='user-profiles-detail',
        parent_lookup_kwargs={'user_pk': 'user__pk'}
    )

    def create(self, validated_data):
        user = User.objects.create_user(validated_data['username'],
                                        validated_data.get('email'),
                                        validated_data['password'])
        return user

    class Meta:
        model = User
        fields = ('username', 'profile', 'email', 'password', 'avatar')
        extra_kwargs = {'password': {'write_only': True}}


class LoginUserSerializer(serializers.Serializer): # DEBUG feature
    username = serializers.CharField()
    password = serializers.CharField()

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
    avatar = serializers.ImageField(source='profile.avatar')
    profile = NestedHyperlinkedRelatedField(
        read_only=True,
        view_name='user-profiles-detail',
        parent_lookup_kwargs={'user_pk': 'user__pk'}
    )

    class Meta:
        model = User
        fields = ('url', 'username', 'profile', 'email', 'password', 'avatar')
        extra_kwargs = {'password': {'write_only': True}}


class TagSerializer(serializers.HyperlinkedModelSerializer):
    questions = serializers.HyperlinkedIdentityField(
        view_name='tag-questions-list',
        lookup_url_kwarg='tag_pk',
        read_only=True
    )
    rating = serializers.IntegerField(read_only=True)

    def create(self, validated_data):
        instance, _ = Tag.objects.get_or_create(**validated_data)
        return instance

    class Meta:
        model = Tag
        fields = ('url', 'name', 'rating', 'questions')
        extra_kwargs = {
            'name': {'validators': []},
        }


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
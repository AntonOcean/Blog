from rest_framework import serializers
from backend.models import User, Tag, Question, Answer, Like


class QuestionSerializer(serializers.HyperlinkedModelSerializer):
    likes = serializers.HyperlinkedIdentityField(
        view_name='question-likes',
        lookup_url_kwarg='question_pk'
    )
    author = serializers.ReadOnlyField(source='author.username')
    answers = serializers.HyperlinkedIdentityField(
        many=True,
        view_name='question-answers-list',
        lookup_url_kwarg='question_pk'
    )
    tags = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name'
     )

    class Meta:
        model = Question
        fields = ('url', 'title', 'long_text', 'author', 'rating', 'answers', 'tags', 'short_text', 'count_answers')


class UserSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = User
        fields = ('url', 'username', 'rating', 'avatar', 'email', 'login')


class TagSerializer(serializers.HyperlinkedModelSerializer):
    questions = serializers.HyperlinkedIdentityField(
        many=True,
        view_name='tag-questions-list',
        lookup_url_kwarg='tag_pk'
    )

    class Meta:
        model = Tag
        fields = ('url', 'name', 'rating', 'questions')


class AnswerSerializer(serializers.HyperlinkedModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    likes = serializers.HyperlinkedIdentityField(
        view_name='answer-likes',
        lookup_url_kwarg='answer_pk'
    )

    class Meta:
        model = Answer
        fields = ('url', 'text', 'author', 'created', 'right_answer', 'rating')


# class LikeSerializer(serializers.HyperlinkedModelSerializer):
#     pass
#
#     class Meta:
#         model = Like
#         fields = '__all__'
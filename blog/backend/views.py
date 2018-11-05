from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

from backend.models import Question, User, Answer, Tag, Like, Profile
from backend.serializers import QuestionSerializer, UserSerializer, AnswerSerializer, TagSerializer, ProfileSerializer

# права досупа, обработка методов, установка автора, вопроса и т.д.
# дохуя блять логики тутачки
# likes это action на вью


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'users': reverse('user-list', request=request, format=format),
        'questions': reverse('question-list', request=request, format=format),
        'tags': reverse('tag-list', request=request, format=format),
        'answers': reverse('answer-list', request=request, format=format)
    })


class QuestionViewSet(viewsets.ModelViewSet):
    #  avtor default
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

    @action(detail=True, methods=['post'])
    def set_like(self, *args, **kwargs):
        user = self.request.user
        question = self.get_object()
        count_like = Like.set_like(question, user)
        return Response({'count_like': count_like})


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()


class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()

    def get_queryset(self):
        user_id = self.kwargs.get('user_pk')
        if user_id:
            return Profile.objects.filter(user_id=user_id)
        return Profile.objects.all()


class AnswerViewSet(viewsets.ModelViewSet):
    # question default
    # avtor default
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer

    @action(detail=True, methods=['post'])
    def set_like(self,  *args, **kwargs):
        user = self.request.user
        question = self.get_object()
        count_like = Like.set_like(question, user)
        return Response({'count_like': count_like})

    @action(detail=True, methods=['put'])
    def mark_as_right(self,  *args, **kwargs):
        user = self.request.user
        answer = self.get_object()
        mark = answer.mark_as_right()
        return Response({'is_right': mark})

    def get_queryset(self):
        question_id = self.kwargs.get('question_pk')
        if question_id:
            return Answer.objects.filter(question_id=question_id)
        return Answer.objects.all()


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    def get_queryset(self):
        question_pk = self.kwargs.get('question_pk')
        if question_pk:
            return Tag.objects.filter(question_id=question_pk)
        return Tag.objects.all()
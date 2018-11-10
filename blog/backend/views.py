from django.urls import reverse
from knox.auth import TokenAuthentication
from knox.models import AuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, viewsets, permissions
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse as rest_reverse

from backend.models import Question, User, Answer, Tag, Like, Profile
from backend.serializers import QuestionSerializer, UserSerializer, AnswerSerializer, TagSerializer, ProfileSerializer, \
    CreateUserSerializer, LoginUserSerializer


# TODO права досупа, обработка методов

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'users': rest_reverse('user-list', request=request, format=format),
        'questions': rest_reverse('question-list', request=request, format=format),
        'tags': rest_reverse('tag-list', request=request, format=format),
        'answers': rest_reverse('answer-list', request=request, format=format),
        'register': rest_reverse('register', request=request, format=format),
        'login': rest_reverse('login', request=request, format=format)
    })


class RegistrationAPI(generics.GenericAPIView):
    serializer_class = CreateUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            # "token": AuthToken.objects.create(user)
        })


class UserAPI(generics.RetrieveAPIView):
    # permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class LoginAPI(generics.GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    serializer_class = LoginUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            # "token": AuthToken.objects.create(user)
        })


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'])
    def set_like(self, *args, **kwargs):
        user = self.request.user
        question = self.get_object()
        count_like = Like.set_like(question, user)
        user.save()
        question.save()
        return Response({'rating': count_like})

    def get_queryset(self):
        tag_pk = self.kwargs.get('tag_pk')
        if tag_pk:
            return Question.objects.filter(tags__id=tag_pk)
        return Question.objects.all()


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
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer

    def perform_create(self, serializer):
        question_id = self.kwargs.get('question_pk')
        if question_id:
            serializer.save(author=self.request.user, question_id=question_id)
            question = Question.objects.get(id=question_id)
            question.count_up()
            question.save()
        else:
            serializer.save()

    @action(detail=True, methods=['post'])
    def set_like(self,  *args, **kwargs):
        user = self.request.user
        question = self.get_object()
        count_like = Like.set_like(question, user)
        return Response({'count_like': count_like})

    @action(detail=True, methods=['put'])
    def mark_as_right(self,  *args, **kwargs):
        answer = self.get_object()
        mark = answer.mark_as_right()
        answer.save()
        return Response({'is_right': mark})

    def get_queryset(self):
        question_id = self.kwargs.get('question_pk')
        if question_id:
            return Answer.objects.filter(question_id=question_id)
        return Answer.objects.all()


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    def add_question(self):
        tag_name = self.request.POST.get('name')
        tag = Tag.objects.get(name=tag_name)
        question_id = self.kwargs.get('question_pk')
        question = Question.objects.get(id=question_id)
        tag.questions.add(question)
        tag.rating_up()
        tag.save()

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args)
        self.add_question()
        return response

    def get_queryset(self):
        question_pk = self.kwargs.get('question_pk')
        if question_pk:
            return Tag.objects.filter(questions__id=question_pk)
        return Tag.objects.all()

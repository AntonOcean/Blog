from django.contrib.auth import login, user_logged_in
from knox.auth import TokenAuthentication
from knox.models import AuthToken
from knox.views import LoginView as KnoxLoginView
from rest_framework.authentication import BasicAuthentication
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.decorators import permission_classes as permission
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, IsAdminUser, AllowAny
from rest_framework import generics, viewsets, permissions
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse as rest_reverse
from rest_framework.views import APIView

from backend.models import Question, User, Answer, Tag, Like, Profile
from backend.permissions import IsQuestionOwner, IsProfileOwner
from backend.serializers import QuestionSerializer, UserSerializer, AnswerSerializer, TagSerializer, ProfileSerializer, \
    LoginUserSerializer, CreateUserSerializer


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'users': rest_reverse('user-list', request=request, format=format),
        'questions': rest_reverse('question-list', request=request, format=format),
        'tags': rest_reverse('tag-list', request=request, format=format),
        'answers': rest_reverse('answer-list', request=request, format=format),
        'profiles': rest_reverse('profile-list', request=request, format=format),
        'register': rest_reverse('register', request=request, format=format),
        'login': rest_reverse('login', request=request, format=format),
        'logout': rest_reverse('logout', request=request, format=format),
        'debug_logout': rest_reverse('debug_logout', request=request, format=format),
    })


class RegistrationAPI(generics.CreateAPIView):
    serializer_class = CreateUserSerializer
    permission_classes = (AllowAny,)
    queryset = User.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)
        })


class LoginView(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = LoginUserSerializer # DEBUG only

    def post(self, request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return super(LoginView, self).post(request, format=None)


class QuestionViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=(IsAuthenticated,))
    def set_like(self, *args, **kwargs):
        user = self.request.user
        question = self.get_object()
        count_like = Like.set_like(question, user)
        user.save()
        question.save()
        return Response({'rating': count_like})

    def get_queryset(self):
        sort_by = self.request.GET.get('sort')
        if sort_by:
            return Question.objects.hot_questions(sort_by)
        tag_pk = self.kwargs.get('tag_pk')
        if tag_pk:
            return Question.objects.filter(tags__id=tag_pk)
        return Question.objects.all()


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (IsAdminUser,)


class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()
    permission_classes = (IsProfileOwner|IsAdminUser,)

    def get_queryset(self):
        user_id = self.kwargs.get('user_pk')
        sort_by = self.request.GET.get('sort')
        limit = self.request.GET.get('limit')
        if sort_by and limit:
            return Profile.objects.top_users(sort_by, int(limit))
        if user_id:
            return Profile.objects.filter(user_id=user_id)
        return Profile.objects.all()


class AnswerViewSet(viewsets.ModelViewSet):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        question_id = self.kwargs.get('question_pk')
        if question_id:
            serializer.save(author=self.request.user, question_id=question_id)
            question = Question.objects.get(id=question_id)
            question.count_up()
            question.save()
        else:
            serializer.save()

    @action(detail=True, methods=['post'], permission_classes=(IsAuthenticated,))
    def set_like(self,  *args, **kwargs):
        user = self.request.user
        question = self.get_object()
        count_like = Like.set_like(question, user)
        user.save()
        question.save()
        return Response({'count_like': count_like})

    @action(detail=True, methods=['post'], permission_classes=(IsQuestionOwner|IsAdminUser,))
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
    permission_classes = (IsAuthenticatedOrReadOnly,)

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
        sort_by = self.request.GET.get('sort')
        limit = self.request.GET.get('limit')
        if sort_by and limit:
            return Tag.objects.top_tags(sort_by, int(limit))
        if question_pk:
            return Tag.objects.filter(questions__id=question_pk)
        return Tag.objects.all()

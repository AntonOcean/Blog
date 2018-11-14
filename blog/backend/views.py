from django.contrib.auth import login, user_logged_out, logout
from django.db.models import Prefetch
from knox.auth import TokenAuthentication
from knox.models import AuthToken
from knox.views import LoginView as KnoxLoginView
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.pagination import CursorPagination
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, IsAdminUser, AllowAny
from rest_framework import generics, viewsets, permissions, status, mixins
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse as rest_reverse
from rest_framework.views import APIView

from backend.models import Question, User, Answer, Tag, Like
from backend.permissions import IsQuestionOwner, IsUserOwner
from backend.serializers import QuestionSerializer, UserSerializer, AnswerSerializer, TagSerializer, ProfileSerializer, \
    LoginUserSerializer, CreateUserSerializer


@api_view(['GET'])
def api_root(request, format=None):
    data = {
        'users': rest_reverse('user-list', request=request, format=format),
        'questions': rest_reverse('question-list', request=request, format=format),
        'tags': rest_reverse('tag-list', request=request, format=format),
        'register': rest_reverse('register', request=request, format=format),
        'login': rest_reverse('login', request=request, format=format),
        'logout': rest_reverse('logout', request=request, format=format),
        'debug_logout': rest_reverse('debug_logout', request=request, format=format),
    }
    if request.user and request.user.is_authenticated:
        data.update({'profile': rest_reverse('user-profile', kwargs={"pk": request.user.id}, request=request, format=format)})
    return Response(data)


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
        }, status=status.HTTP_201_CREATED)


class LoginView(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = LoginUserSerializer # DEBUG only

    def post(self, request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return super(LoginView, self).post(request, format=None)


class LogoutView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        request._auth.delete()
        user_logged_out.send(sender=request.user.__class__,
                             request=request, user=request.user)
        logout(request) # DEBUG only
        return Response(None, status=status.HTTP_204_NO_CONTENT)


class QuestionViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Question.objects.prefetch_related('tags', 'author')
    serializer_class = QuestionSerializer
    pagination_class = CursorPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        tags = serializer.initial_data.get('tags', [])
        for name_tag in tags:
            Tag.objects.get_or_create(name=name_tag)

        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['put'], permission_classes=(IsAuthenticated,))
    def set_like(self, *args, **kwargs):
        user = self.request.user
        question = self.get_object()
        Like.set_like(question, user)
        return Response(
            QuestionSerializer(self.get_object(), context=self.get_serializer_context()).data,
            status=status.HTTP_200_OK
        )

    def get_queryset(self):
        sort_by = self.request.GET.get('sort')
        queryset = super().get_queryset()
        if sort_by:
            return queryset.hot_questions(sort_by)
        tag_pk = self.kwargs.get('tag_pk')
        if tag_pk:
            return queryset.filter(tags__id=tag_pk)
        return queryset


class UserListView(generics.ListAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        sort_by = self.request.GET.get('sort')
        queryset = super().get_queryset()
        limit = self.request.GET.get('limit')
        if sort_by and limit:
            return User.objects.top_users(sort_by, int(limit))
        return queryset


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    queryset = User.objects.all()
    permission_classes = (IsUserOwner|IsAdminUser,)


class AnswerViewSet(viewsets.ModelViewSet):
    queryset = Answer.objects.prefetch_related('author')
    serializer_class = AnswerSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        question_id = self.kwargs.get('question_pk')
        serializer.save(author=self.request.user, question_id=question_id)

    @action(detail=True, methods=['put'], permission_classes=(IsAuthenticated,))
    def set_like(self,  *args, **kwargs):
        user = self.request.user
        answer = self.get_object()
        Like.set_like(answer, user)
        return Response(
            AnswerSerializer(self.get_object(), context=self.get_serializer_context()).data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['put'], permission_classes=(IsQuestionOwner|IsAdminUser,))
    def mark_as_right(self,  *args, **kwargs):
        answer = self.get_object()
        mark = answer.mark_as_right()
        answer.save()
        return Response(
            AnswerSerializer(answer, context=self.get_serializer_context()).data,
            status=status.HTTP_200_OK
        )

    def get_queryset(self):
        question_id = self.kwargs.get('question_pk')
        queryset = super().get_queryset()
        if question_id:
            return queryset.filter(question_id=question_id)
        return queryset


class TagViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        sort_by = self.request.GET.get('sort')
        limit = self.request.GET.get('limit')
        queryset = super().get_queryset()
        if sort_by and limit:
            return queryset.top_tags(sort_by, int(limit))
        return queryset

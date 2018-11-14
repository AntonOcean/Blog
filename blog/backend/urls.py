from django.urls import path, include
from rest_framework_nested import routers

from backend import views

router = routers.SimpleRouter()

router.register(r'questions', views.QuestionViewSet)
router.register(r'answers', views.AnswerViewSet)
router.register(r'tags', views.TagViewSet)

question_router = routers.NestedSimpleRouter(router, r'questions', lookup='question')
question_router.register(r'answers', views.AnswerViewSet, base_name='question-answers')

tag_router = routers.NestedSimpleRouter(router, r'tags', lookup='tag')
tag_router.register(r'questions', views.QuestionViewSet, base_name='tag-questions')


urlpatterns = [
    path('', views.api_root),
    path('', include(router.urls)),
    path('', include(question_router.urls)),
    path('', include(tag_router.urls)),
    path('users/<int:pk>/profile/', views.ProfileView.as_view(), name='user-profile'),
    path('users/', views.UserListView.as_view(), name='user-list')
]

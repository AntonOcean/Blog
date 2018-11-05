from django.urls import path, include
# from rest_framework import renderers, routers
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.authtoken import views as drf_views
from rest_framework_nested import routers

from backend import views

router = routers.SimpleRouter()
router.register(r'users', views.UserViewSet)
router.register(r'questions', views.QuestionViewSet)
router.register(r'answers', views.AnswerViewSet)
router.register(r'tags', views.TagViewSet)
router.register(r'profiles', views.ProfileViewSet)
# urlpatterns = router.urls

question_router = routers.NestedSimpleRouter(router, r'questions', lookup='question')
question_router.register(r'answers', views.AnswerViewSet, base_name='question-answers')
# question_router.register(r'tags', views.TagViewSet, base_name='question-tags')

tag_router = routers.NestedSimpleRouter(router, r'tags', lookup='tag')
tag_router.register(r'questions', views.QuestionViewSet, base_name='tag-questions')

user_router = routers.NestedSimpleRouter(router, r'users', lookup='user')
user_router.register(r'profile', views.ProfileViewSet, base_name='user-profile')


urlpatterns = [
    path('', views.api_root),
    path('', include(router.urls)),
    path('', include(question_router.urls)),
    path('', include(tag_router.urls)),
    path('', include(user_router.urls)),
    path('auth/', drf_views.obtain_auth_token, name='auth')
]

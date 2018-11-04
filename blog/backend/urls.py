from django.urls import path, include
from rest_framework import renderers
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns

from backend import views

urlpatterns = [
    path('questions/', views.QuestionList.as_view()),

]
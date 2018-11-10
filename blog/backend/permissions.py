from django.contrib.auth.models import User
from rest_framework import permissions

from backend.models import Question


class IsOwnerOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user


class IsQuestionOwner(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            question = Question.objects.get(id=view.kwargs.get('pk'))
            return question.author.id == request.user.id
        return False


class IsOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
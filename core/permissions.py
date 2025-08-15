from rest_framework.permissions import BasePermission

from core.models import Quiz


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True

        return obj.owner == request.user


class IsQuizOwner(BasePermission):

    def has_permission(self, request, view):
        quiz_id = view.kwargs.get('quiz_id')
        if quiz_id:
            try:
                quiz = Quiz.objects.get(id=quiz_id)
                return quiz.owner == request.user
            except Quiz.DoesNotExist:
                return False
        return False

from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import *
from .serializers import *

class QuizListAPIView(generics.ListAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = (IsAuthenticated,)

class QuizDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = QuizSerializer
    permission_classes = (IsAuthenticated,)
    def get_queryset(self):
        return Quiz.objects.filter(user=self.request.user)

class QuestionListAPIView(generics.ListAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = (IsAuthenticated,)

class QuizQuestionDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = QuestionSerializer
    permission_classes = (IsAuthenticated,)
    def get_queryset(self):
        return Question.objects.filter(user=self.request.user, quiz=self.kwargs['quiz_id'])

class QuizQuestionsListAPIView(generics.ListAPIView):
    serializer_class = QuestionSerializer
    permission_classes = (IsAuthenticated,)
    def get_queryset(self):
        return Question.objects.filter(quiz=self.kwargs['quiz_id'])
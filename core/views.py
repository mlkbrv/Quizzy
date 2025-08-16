from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from .models import *
from .serializers import *
from rest_framework.pagination import PageNumberPagination
from .permissions import *
from .filters import QuestionsFilter

class QuizListAPIView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPagination
    pagination_class.page_size = 3
    pagination_class.page_query_param = 'pagenum'
    pagination_class.page_size_query_param = 'size'
    pagination_class.max_page_size = 10
    def get_queryset(self):
        return Quiz.objects.order_by('pk')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return QuizCreateSerializer
        return QuizSerializer
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class QuizDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = QuizSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    
    def get_queryset(self):
        return Quiz.objects.all()


class QuestionListAPIView(generics.ListAPIView):
    queryset = Question.objects.order_by('pk')
    serializer_class = QuestionSerializer
    permission_classes = (IsAuthenticated,)


class QuizQuestionDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = QuestionSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Question.objects.filter(quiz=self.kwargs['quiz_id'])
    
    def check_object_permissions(self, request, obj):
        super().check_object_permissions(request, obj)
        if request.method not in ['GET', 'HEAD', 'OPTIONS']:
            if obj.quiz.owner != request.user:
                raise PermissionDenied("Вы можете изменять вопросы только в своих квизах")


class QuizQuestionsListAPIView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    filterset_class = QuestionsFilter

    def get_queryset(self):
        return Question.objects.filter(quiz=self.kwargs['quiz_id']).order_by('pk')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return QuestionCreateSerializer
        return QuestionSerializer
    
    def perform_create(self, serializer):
        quiz_id = self.kwargs['quiz_id']
        quiz = Quiz.objects.get(id=quiz_id)
        
        if quiz.owner != self.request.user:
            raise PermissionDenied("Вы можете создавать вопросы только в своих квизах")
        
        serializer.save(quiz=quiz)


class AnswerOptionListAPIView(generics.ListCreateAPIView):
    serializer_class = AnswerOptionSerializer
    permission_classes = (IsAuthenticated,)
    
    def get_queryset(self):
        return AnswerOption.objects.filter(question=self.kwargs['question_id'])
    
    def perform_create(self, serializer):
        question_id = self.kwargs['question_id']
        question = Question.objects.get(id=question_id)
        
        if question.quiz.owner != self.request.user:
            raise PermissionDenied("Вы можете создавать варианты ответов только в своих квизах")
        
        serializer.save(question=question)


class AnswerOptionDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AnswerOptionSerializer
    permission_classes = (IsAuthenticated,)
    
    def get_queryset(self):
        return AnswerOption.objects.filter(question=self.kwargs['question_id'])
    
    def check_object_permissions(self, request, obj):
        super().check_object_permissions(request, obj)
        if request.method not in ['GET', 'HEAD', 'OPTIONS']:
            if obj.question.quiz.owner != request.user:
                raise PermissionDenied("Вы можете изменять варианты ответов только в своих квизах")
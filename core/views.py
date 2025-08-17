import datetime
from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import *
from .serializers import *
from rest_framework.pagination import PageNumberPagination
from .permissions import *
from .filters import QuestionsFilter


class QuizListAPIView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPagination

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
                raise PermissionDenied("You can only edit questions in your quizzes.")


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
            raise PermissionDenied("You can only create questions in your quizzes.")

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
            raise PermissionDenied("You can only create answer options in your quizzes.")

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
                raise PermissionDenied("You can only change answer options in your quizzes.")


class QuizStartAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        quiz_id = self.kwargs['pk']
        quiz = Quiz.objects.get(id=quiz_id)
        
        attempt = Attempt.objects.filter(
            quiz=quiz,
            user=request.user,
            completed_at__isnull=True,
        ).first()

        if attempt:
            serializer = AttemptSerializer(attempt)
            return Response(serializer.data, status=status.HTTP_200_OK)

        attempt = Attempt.objects.create(
            quiz=quiz,
            user=request.user,
        )
        serializer = AttemptSerializer(attempt)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class QuizFinishAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        quiz_id = self.kwargs['pk']
        quiz = Quiz.objects.get(id=quiz_id)
        
        attempt = Attempt.objects.filter(
            quiz=quiz,
            user=request.user,
            completed_at__isnull=True,
        ).first()
        
        if not attempt:
            return Response({"error": "No active attempts."}, status=status.HTTP_400_BAD_REQUEST)

        answer_data = request.data.get("answers", [])

        if not answer_data:
            return Response({"error": "No answer data."}, status=status.HTTP_400_BAD_REQUEST)

        score = 0
        for answer in answer_data:
            try:
                question = Question.objects.get(id=answer["question_id"], quiz=quiz)
                option = AnswerOption.objects.get(id=answer["option_id"], question=question)
            except (Question.DoesNotExist, AnswerOption.DoesNotExist):
                continue
            UserAnswer.objects.update_or_create(
                attempt=attempt,
                question=question,
                defaults={"select": option}
            )

            if option.is_correct:
                score += question.score

        attempt.score = score
        attempt.completed_at = datetime.datetime.now()
        attempt.save()

        serializer = AttemptSerializer(attempt)
        return Response(serializer.data, status=status.HTTP_200_OK)

from django.urls import path
from .views import *

urlpatterns = [
    path('', QuizListAPIView.as_view(), name='quiz-list'),
    path('<int:pk>/', QuizDetailAPIView.as_view(), name='quiz-detail'),
    path('<int:pk>/start/', QuizStartAPIView.as_view(), name='quiz-start'),
    path('<int:pk>/finish/', QuizFinishAPIView.as_view(), name='quiz-finish'),
    path('questions/', QuestionListAPIView.as_view(), name='question-list'),
    path('<int:quiz_id>/questions/', QuizQuestionsListAPIView.as_view(), name='quiz-questions-list'),
    path('<int:quiz_id>/questions/<int:pk>/', QuizQuestionDetailAPIView.as_view(), name='quiz-question-detail'),
    path('<int:quiz_id>/questions/<int:question_id>/options/', AnswerOptionListAPIView.as_view(),
         name='answer-options-list'),
    path('<int:quiz_id>/questions/<int:question_id>/options/<int:pk>/', AnswerOptionDetailAPIView.as_view(),
         name='answer-option-detail'),
]

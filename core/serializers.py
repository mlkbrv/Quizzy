from rest_framework import serializers
from .models import Question,Quiz,Attempt,AnswerOption,UserAnswer

class AnswerOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerOption
        fields = [
            'id',
            'answer',
            'is_correct',
        ]

class QuestionSerializer(serializers.ModelSerializer):
    options = AnswerOptionSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = [
            'id',
            'text',
            'score',
            'options',
        ]

class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    owner = serializers.StringRelatedField()

    class Meta:
        model = Quiz
        fields = [
            'id',
            'title',
            'description',
            'owner',
            'created_at',
            'is_active',
            'questions',
        ]

class UserAnswerSerializer(serializers.ModelSerializer):
    question_text = serializers.CharField(source='question.text', read_only=True)
    selected_answer = serializers.CharField(source='select.answer', read_only=True)
    is_correct = serializers.BooleanField(source='select.is_correct', read_only=True)

    class Meta:
        model = UserAnswer
        fields = [
            'question_text',
            'selected_answer',
            'is_correct',
        ]

class AttemptSerializer(serializers.ModelSerializer):
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    answers = UserAnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Attempt
        fields = [
            'id',
            'quiz_title',
            'user_username',
            'started_at',
            'completed_at',
            'score',
            'answers',
        ]
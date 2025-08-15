from rest_framework import serializers
from .models import Question, Quiz, Attempt, AnswerOption, UserAnswer


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


class QuestionCreateSerializer(serializers.ModelSerializer):
    options = AnswerOptionSerializer(many=True)

    class Meta:
        model = Question
        fields = [
            'text',
            'score',
            'options',
        ]

    def create(self, validated_data):
        options_data = validated_data.pop('options')
        question = Question.objects.create(**validated_data)
        
        for option_data in options_data:
            AnswerOption.objects.create(question=question, **option_data)
        
        return question


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    owner = serializers.StringRelatedField()
    owner_id = serializers.IntegerField(source='owner.id', read_only=True)
    is_owner = serializers.SerializerMethodField()
    questions_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Quiz
        fields = [
            'id',
            'title',
            'description',
            'owner',
            'owner_id',
            'is_owner',
            'created_at',
            'is_active',
            'questions',
            'questions_count',
        ]
    
    def get_is_owner(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return obj.owner == request.user
        return False
    
    def get_questions_count(self, obj):
        return obj.questions.count()


class QuizCreateSerializer(serializers.ModelSerializer):
    questions = QuestionCreateSerializer(many=True, required=False)

    class Meta:
        model = Quiz
        fields = [
            'title',
            'description',
            'is_active',
            'questions',
        ]

    def create(self, validated_data):
        questions_data = validated_data.pop('questions', [])
        quiz = Quiz.objects.create(**validated_data)
        
        for question_data in questions_data:
            options_data = question_data.pop('options', [])
            question = Question.objects.create(quiz=quiz, **question_data)
            
            for option_data in options_data:
                AnswerOption.objects.create(question=question, **option_data)
        
        return quiz


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
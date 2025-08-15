from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Question, Quiz, Attempt, AnswerOption, UserAnswer


class AnswerOptionInline(admin.TabularInline):
    model = AnswerOption
    extra = 4
    fields = ('answer', 'is_correct')
    ordering = ('id',)


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ('text', 'score')
    ordering = ('id',)
    show_change_link = True


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'question_count', 'is_active', 'created_at', 'attempts_count')
    list_filter = ('is_active', 'created_at', 'owner')
    search_fields = ('title', 'description', 'owner__username')
    list_editable = ('is_active',)
    readonly_fields = ('created_at', 'question_count', 'attempts_count')
    inlines = [QuestionInline]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'owner')
        }),
        ('Статус', {
            'fields': ('is_active', 'created_at')
        }),
        ('Статистика', {
            'fields': ('question_count', 'attempts_count'),
            'classes': ('collapse',)
        }),
    )
    
    def question_count(self, obj):
        return obj.questions.count()
    question_count.short_description = 'Количество вопросов'
    
    def attempts_count(self, obj):
        return obj.attempts.count()
    attempts_count.short_description = 'Количество попыток'


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text_preview', 'quiz', 'score', 'options_count', 'correct_options_count')
    list_filter = ('quiz', 'score', 'quiz__owner')
    search_fields = ('text', 'quiz__title')
    list_editable = ('score',)
    inlines = [AnswerOptionInline]
    
    fieldsets = (
        ('Вопрос', {
            'fields': ('quiz', 'text', 'score')
        }),
    )
    
    def text_preview(self, obj):
        return obj.text[:100] + '...' if len(obj.text) > 100 else obj.text
    text_preview.short_description = 'Текст вопроса'
    
    def options_count(self, obj):
        return obj.options.count()
    options_count.short_description = 'Вариантов ответа'
    
    def correct_options_count(self, obj):
        return obj.options.filter(is_correct=True).count()
    correct_options_count.short_description = 'Правильных ответов'


@admin.register(AnswerOption)
class AnswerOptionAdmin(admin.ModelAdmin):
    list_display = ('answer', 'question_preview', 'quiz_title', 'is_correct')
    list_filter = ('is_correct', 'question__quiz', 'question__quiz__owner')
    search_fields = ('answer', 'question__text', 'question__quiz__title')
    list_editable = ('is_correct',)
    
    def question_preview(self, obj):
        return obj.question.text[:50] + '...' if len(obj.question.text) > 50 else obj.question.text
    question_preview.short_description = 'Вопрос'
    
    def quiz_title(self, obj):
        return obj.question.quiz.title
    quiz_title.short_description = 'Тест'


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'score', 'started_at', 'completed_at', 'completion_status')
    list_filter = ('quiz', 'started_at', 'completed_at', 'user')
    search_fields = ('user__username', 'quiz__title')
    readonly_fields = ('started_at', 'score')
    date_hierarchy = 'started_at'
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'quiz', 'score')
        }),
        ('Время', {
            'fields': ('started_at', 'completed_at')
        }),
    )
    
    def completion_status(self, obj):
        if obj.completed_at:
            return format_html('<span style="color: green;">✓ Завершено</span>')
        else:
            return format_html('<span style="color: orange;">⟳ В процессе</span>')
    completion_status.short_description = 'Статус'


@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'question_preview', 'selected_answer', 'is_correct', 'attempt_date')
    list_filter = ('select__is_correct', 'attempt__quiz', 'attempt__started_at')
    search_fields = ('attempt__user__username', 'question__text', 'select__answer')
    readonly_fields = ('attempt', 'question', 'select')
    
    def user(self, obj):
        return obj.attempt.user
    user.short_description = 'Пользователь'
    
    def quiz(self, obj):
        return obj.attempt.quiz
    quiz.short_description = 'Тест'
    
    def question_preview(self, obj):
        return obj.question.text[:50] + '...' if len(obj.question.text) > 50 else obj.question.text
    question_preview.short_description = 'Вопрос'
    
    def selected_answer(self, obj):
        return obj.select.answer
    selected_answer.short_description = 'Выбранный ответ'
    
    def is_correct(self, obj):
        return obj.select.is_correct
    is_correct.short_description = 'Правильно'
    
    def attempt_date(self, obj):
        return obj.attempt.started_at.date()
    attempt_date.short_description = 'Дата попытки'
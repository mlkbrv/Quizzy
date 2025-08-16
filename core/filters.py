import django_filters
from .models import Question
class QuestionsFilter(django_filters.rest_framework.FilterSet):
    class Meta:
        model = Question
        fields = {
            'text': ['iexact','icontains'],
            'score': ['exact','gt','gte','lt','lte','range'],
        }
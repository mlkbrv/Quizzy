from django.contrib import admin
from .models import Question,Quiz,Attempt,AnswerOption,UserAnswer

admin.site.register(Question)
admin.site.register(Quiz)
admin.site.register(Attempt)
admin.site.register(AnswerOption)
admin.site.register(UserAnswer)
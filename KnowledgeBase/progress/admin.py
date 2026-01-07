from django.contrib import admin
from .models import LessonProgress, QuizAttempt, StudentAnswer

# Register your models here.
admin.site.register(LessonProgress)
admin.site.register(QuizAttempt)
admin.site.register(StudentAnswer)
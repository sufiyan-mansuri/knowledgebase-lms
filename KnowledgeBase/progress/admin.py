from django.contrib import admin
from .models import LessonProgress, QuizAttempt, StudentAnswer

@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ('id', 'lesson', 'student', 'is_completed', 'completed_at', 'created_at', 'updated_at')

@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'quiz', 'score', 'created_at', 'updated_at')

@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'attempt', 'question', 'selected_option', 'created_at', 'updated_at')
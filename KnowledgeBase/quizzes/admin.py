from django.contrib import admin
from .models import Quiz, Question, Option

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('id', 'lesson', 'total_marks', 'status', 'created_at', 'updated_at')

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'quiz', 'question', 'marks', 'order', 'created_at', 'updated_at')

@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'option', 'is_correct', 'order', 'created_at', 'updated_at')

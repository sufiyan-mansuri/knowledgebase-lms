from django.contrib import admin
from .models import Quiz, Question, Option

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ('question', 'marks', 'order')

class OptionInline(admin.TabularInline):
    model = Option
    extra = 1
    fields = ('option', 'is_correct', 'order')

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('id', 'lesson', 'total_marks', 'status', 'created_at', 'updated_at')
    search_fields = ('lesson__title',)
    list_filter = ('status',)
    readonly_fields = ('created_at',)
    inlines=[QuestionInline]

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'quiz', 'question', 'marks', 'order', 'created_at', 'updated_at')
    search_fields = ('quiz__lesson__title', 'question')
    list_filter = ('quiz',)
    readonly_fields = ('created_at',)
    inlines=[OptionInline]

@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'option', 'is_correct', 'order', 'created_at', 'updated_at')
    search_fields = ('question__question', 'option')
    list_filter = ('question', 'is_correct')
    readonly_fields = ('created_at',)
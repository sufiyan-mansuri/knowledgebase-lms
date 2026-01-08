from django.contrib import admin
from . import models
from django.contrib.auth import get_user_model
from django import forms
from lessons.models import Lesson

User = get_user_model()

class CourseInline(admin.TabularInline):
    model = models.Course
    extra = 1
    fields = ('title', 'description', 'thumbnail', 'instructor', 'status',)

class ModuleInline(admin.TabularInline):
    model = models.Module
    extra = 1 
    fields = ('title', 'order')

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1 
    fields = ('title', 'content', 'video_url', 'order')

@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at', 'updated_at')
    search_fields = ('name',)
    readonly_fields = ('created_at',)
    inlines = [CourseInline]

class CourseAdminForm(forms.ModelForm):
    class Meta:
        model = models.Course
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['instructor'].queryset = User.objects.filter(role='instructor')

@admin.register(models.Course)
class CourseAdmin(admin.ModelAdmin):
    form = CourseAdminForm
    list_display = ('id', 'title', 'description', 'category', 'thumbnail', 'instructor', 'status', 'slug', 'created_at', 'updated_at')
    search_fields = ('title', 'description', 'category__name')
    list_filter = ('category', 'instructor', 'status')
    readonly_fields = ('created_at',)
    inlines = [ModuleInline]

@admin.register(models.Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'course', 'order', 'created_at', 'updated_at')
    search_fields = ('title', 'course__name')
    list_filter = ('course',)
    readonly_fields = ('created_at',)
    inlines = [LessonInline]
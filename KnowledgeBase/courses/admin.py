from django.contrib import admin
from . import models
from django.contrib.auth import get_user_model
from django import forms

User = get_user_model()

@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at', 'updated_at')

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

@admin.register(models.Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'course', 'order', 'created_at', 'updated_at')
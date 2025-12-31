from django.contrib import admin
from . import models
from django.contrib.auth import get_user_model
from django import forms

User = get_user_model()

# Register your models here.
admin.site.register(models.Category)

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


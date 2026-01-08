from django.contrib import admin
from .models import Enrollment

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'course', 'student', 'created_at', 'updated_at')
    search_fields = ('course__title', 'student__username')
    list_filter = ('course', 'student',)
    readonly_fields = ('created_at',)
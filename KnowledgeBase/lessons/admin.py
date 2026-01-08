from django.contrib import admin
from .models import Lesson

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'short_content', 'video_url', 'module', 'order', 'created_at', 'updated_at')
    search_fields = ('title', 'content', 'module__title')
    list_filter = ('module',)
    readonly_fields = ('created_at',)

    @admin.display(description='Content Preview')
    def short_content(self, obj):
        if obj.content and len(obj.content) > 100:
            return obj.content[:100] + '...'
        return obj.content

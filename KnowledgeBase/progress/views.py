from django.shortcuts import render, redirect, get_object_or_404
from .models import LessonProgress
from django.utils import timezone
from lessons.models import Lesson
from users.decorators import allowed_users

# Create your views here.
@allowed_users('Students')
def mark_lesson_as_complete(request, slug, module_id, lesson_id):
    user = request.user 
    lesson = get_object_or_404(Lesson, id=lesson_id)

    progress, created = LessonProgress.objects.get_or_create(
        student=user,
        lesson=lesson
    )

    if not progress.is_completed:
        progress.is_completed = True
        progress.completed_at = timezone.now()
        progress.save()

    return redirect('lessons:lesson_detail', slug, module_id, lesson_id)
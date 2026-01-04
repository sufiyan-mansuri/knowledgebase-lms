from django.db import models
from lessons.models import Lesson
from users.models import User

# Create your models here.
class LessonProgress(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['lesson', 'student']
        verbose_name_plural = "Lesson Progress"

    def __str__(self):
        return f"Progress of {self.student.username} in {self.lesson.title}: {self.completed_at}"
    
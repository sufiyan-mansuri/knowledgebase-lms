from django.db import models
from courses.models import Course
from users.models import User
from lessons.models import Lesson

class Enrollment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    last_accessed_lesson = models.ForeignKey(Lesson, blank=True, null=True, on_delete=models.SET_NULL, related_name='last_viewed_by')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student.full_name} enrolled in {self.course.title} at {self.created_at}" 
    
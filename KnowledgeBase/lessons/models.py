from django.db import models
from courses.models import Module

# Create your models here.
class Lesson(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    video_url = models.URLField(max_length=500, blank=True, null=True)
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    order = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']
        constraints = [
            models.UniqueConstraint(
                fields=['module', 'order'],
                name='unique_lesson_order_per_module'
            )
        ]

    def __str__(self):
        return f"{self.title} - {self.module.title}"

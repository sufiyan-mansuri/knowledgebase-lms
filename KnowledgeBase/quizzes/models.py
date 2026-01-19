from django.db import models
from lessons.models import Lesson

# Create your models here.
class Quiz(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('locked', 'Locked'),
    )

    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name='quizzes')
    total_marks = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Quizzes'

    def __str__(self):
        return f"Quiz for {self.lesson}"
    
class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question = models.TextField()
    marks = models.PositiveIntegerField(default=1)
    order = models.PositiveSmallIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']
        constraints = [
            models.UniqueConstraint(
                fields=['quiz', 'order'],
                name='unique_question_order_per_quiz'
            )
        ]

    def options_count(self):
        return self.options.count()

    def correct_options_count(self):
        return self.options.filter(is_correct=True).count()

    def is_valid_question(self):
        return (
            self.options_count() >= 2 and
            self.correct_options_count() == 1
        )

    def __str__(self):
        return f'{self.question}'

class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    option = models.TextField()
    is_correct = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']
        constraints = [
            models.UniqueConstraint(
                fields=['question', 'order'],
                name='unique_option_order_per_question'
            )
        ]

    def __str__(self):
        return f'{self.option}'

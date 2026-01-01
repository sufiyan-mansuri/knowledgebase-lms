from django.db import models
from users import models as userModels
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.core.exceptions import ValidationError

User = get_user_model()

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=256, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name
    
class Course(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published')
    )

    title = models.CharField(max_length=256)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='courses')
    thumbnail = models.ImageField(upload_to='course_thumbnails/')
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    slug = models.SlugField(unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Courses'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.instructor.username}"
    
class Module(models.Model):
    title = models.CharField(max_length=256)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    order = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']
        constraints = [
            models.UniqueConstraint(
                fields=['course', 'order'],
                name='unique_module_order_per_course'
            )
        ]

    def clean(self):
        if self.order <= 0:
            raise ValidationError({'order': 'Order must be a positive number.'})

    def __str__(self):
        return f"{self.title} - {self.course.title}"
from django.shortcuts import render, get_object_or_404, redirect
from .models import Enrollment
from courses.models import Course
from django.core.exceptions import PermissionDenied
from users.decorators import allowed_users
from django.views.decorators.cache import never_cache

# Create your views here.
@never_cache
@allowed_users(['Students'])
def enroll(request, slug):
    user = request.user 
    course = get_object_or_404(Course, slug=slug)
    
    if user.is_superuser:
        raise PermissionDenied('Admin cannot enroll in courses')

    if course.status != 'published':
        raise PermissionDenied('Cannot enroll in unpublished course')

    if user.groups.filter(name='Instructors').exists():
        raise PermissionDenied('Instructors cannot enroll')

    Enrollment.objects.get_or_create(course=course, student=user)          
    
    return redirect('courses:course_detail', slug=course.slug)


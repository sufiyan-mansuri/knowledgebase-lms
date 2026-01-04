from django.shortcuts import render, get_object_or_404, redirect
from .models import Enrollment
from courses.models import Course
from django.core.exceptions import PermissionDenied
from users.decorators import allowed_users


# Create your views here.
@allowed_users(['Students'])
def enroll(request, slug):
    user = request.user 
    course = get_object_or_404(Course, slug=slug)
    
    if course.status == "published" and course.instructor != user:
        Enrollment.objects.get_or_create(course=course, student=user)
    else:
        PermissionDenied

    return redirect('courses:course_detail', slug=course.slug)


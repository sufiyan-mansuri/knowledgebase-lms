from django.shortcuts import render
from courses.models import Course
from enrollments.models import Enrollment

# Create your views here.
def home(request):
    return render(request, 'core/home.html')

def course_catalog(request):
    user = request.user
    published_courses = Course.objects.filter(status='published')
    user_enrolled_courses = Enrollment.objects.filter(student=user).values_list('course_id', flat=True)

    data = {
        'published_courses': published_courses,
        'user_enrolled_courses': user_enrolled_courses,
    }

    return render(request, 'core/course_catalog.html', data)

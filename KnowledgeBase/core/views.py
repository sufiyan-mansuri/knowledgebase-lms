from django.shortcuts import render
from courses.models import Course

# Create your views here.
def home(request):
    return render(request, 'core/home.html')

def course_catalog(request):
    published_courses = Course.objects.filter(status='published')

    data = {
        'published_courses': published_courses,
    }

    return render(request, 'core/course_catalog.html', data)

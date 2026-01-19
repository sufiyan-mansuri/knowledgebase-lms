from django.shortcuts import render
from courses.models import Course, Category
from enrollments.models import Enrollment

# Create your views here.
def home(request):
    featured_courses = Course.objects.filter(is_featured=True, status='published')

    context = {
        'featured_courses': featured_courses,
    }

    return render(request, 'core/home.html', context)

def course_catalog(request):
    user = request.user
    published_courses = Course.objects.filter(status='published')
    
    is_instructor = False
    if user.groups.filter(name='Instructors').exists():
        is_instructor = True

    if user.is_authenticated:
        user_enrolled_courses = Enrollment.objects.filter(student=user).values_list('course_id', flat=True)
    else:
        user_enrolled_courses = []

    categories = Category.objects.all()

    selected_category = request.GET.get('category')

    if selected_category:
        published_courses = published_courses.filter(category__name=selected_category)

    data = {
        'published_courses': published_courses,
        'user_enrolled_courses': user_enrolled_courses,
        'categories': categories,
        'selected_category': selected_category,
        'is_instructor': is_instructor,
    }

    return render(request, 'core/course_catalog.html', data)

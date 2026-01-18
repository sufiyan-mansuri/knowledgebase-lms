from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from users.decorators import allowed_users
from courses.models import Course
from enrollments.models import Enrollment
from lessons.models import Lesson
from progress.models import LessonProgress, QuizAttempt
from django.views.decorators.cache import never_cache

# Create your views here.
@never_cache
@allowed_users(['Students'])
def student_dashboard(request):
    student = request.user
    enrollments = Enrollment.objects.select_related('course').filter(student=student)
    total_enrollments = 0
    total_completed_lessons = 0

    enrolled_course_details = []
    for enrollment in enrollments:
        course = enrollment.course
        total_enrollments += 1

        total_lessons = Lesson.objects.filter(module__course=course).count()

        completed_lessons = LessonProgress.objects.filter(
            student=student,
            lesson__module__course=course,
            is_completed=True
        ).count()

        total_completed_lessons += completed_lessons 

        enrolled_course_details.append({
            'course': course,
            'user_progress': (completed_lessons/total_lessons)*100,
        })
    
    quiz_attempts = QuizAttempt.objects.filter(
        student=student
    )

    context = {
        'enrolled_course_details': enrolled_course_details,
        'quiz_attempts': quiz_attempts,
        'total_enrollments': total_enrollments,
        'total_completed_lessons': total_completed_lessons,
    }

    return render(request, 'dashboard/student_dashboard.html', context)

@never_cache
@allowed_users(['Instructors'])
def instructor_dashboard(request):
    instructor = request.user
    courses = Course.objects.filter(instructor=request.user.id)
    total_course_count = courses.count()
    total_enrollment_count = Enrollment.objects.filter(course__instructor=instructor).count()
    published_course_count = courses.filter(status='published').count()

    course_details = []
    for course in courses:
        total_enrollments = Enrollment.objects.filter(course=course, course__instructor=instructor).count()
        course_module_count = course.modules.count()
        course_lesson_count = Lesson.objects.filter(module__course=course).count()

        course_details.append({
            'course': course,
            'total_enrollments': total_enrollments,
            'course_module_count': course_module_count,
            'course_lesson_count': course_lesson_count,
        })

    context = {
        'course_details': course_details,
        'total_course_count': total_course_count,
        'total_enrollment_count': total_enrollment_count,
        'published_course_count': published_course_count,
    }

    return render(request, 'dashboard/instructor_dashboard.html', context)
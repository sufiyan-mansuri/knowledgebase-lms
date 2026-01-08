from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from users.decorators import allowed_users
from courses.models import Course
from enrollments.models import Enrollment
from lessons.models import Lesson
from progress.models import LessonProgress, QuizAttempt

# Create your views here.
@allowed_users(['Students'])
def student_dashboard(request):
    student = request.user
    enrollments = Enrollment.objects.select_related('course').filter(student=student)
    enrolled_course_details = []
    for enrollment in enrollments:
        course = enrollment.course

        total_lessons = Lesson.objects.filter(module__course=course).count()

        completed_lessons = LessonProgress.objects.filter(
            student=student,
            lesson__module__course=course,
            is_completed=True
        ).count()

        enrolled_course_details.append({
            'course': course,
            'user_progress': (completed_lessons/total_lessons)*100,
        })
    
    quiz_attempts = QuizAttempt.objects.filter(
        student=student
    )

    context = {
        'enrolled_course_details': enrolled_course_details,
        'quiz_attempts': quiz_attempts
    }

    return render(request, 'dashboard/student_dashboard.html', context)

@allowed_users(['Instructors'])
def instructor_dashboard(request):
    instructor = request.user
    courses = Course.objects.filter(instructor=request.user.id)
    
    course_details = []
    for course in courses:
        total_enrollments = Enrollment.objects.filter(course=course, course__instructor=instructor).count()

        course_details.append({
            'course': course,
            'total_enrollments': total_enrollments
        })

    context = {
        'course_details': course_details,
    }

    return render(request, 'dashboard/instructor_dashboard.html', context)
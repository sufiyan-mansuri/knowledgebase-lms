from django.core.exceptions import PermissionDenied
from enrollments.models import Enrollment

class InstructorRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        user = request.user

        if not user.is_authenticated:
            raise PermissionDenied
        
        if not (user.is_superuser or user.groups.filter(name='Instructors').exists()):
            raise PermissionDenied
        
        return super().dispatch(request, *args, **kwargs)
    
class StudentRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        user = request.user

        if not user.is_authenticated or user.groups.filter(name='Students').exists():
            raise PermissionDenied
        
        return super().dispatch(request, *args, **kwargs)
    
class EnrollmentRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        course = self.course
        user = request.user

        if not Enrollment.objects.filter(course=course, student=user).exists():
            raise PermissionDenied
        
        return super().dispatch(request, *args, **kwargs)
    
class QuizEditableMixin:
    def dispatch(self, request, *args, **kwargs):
        if self.quiz.status == 'locked':
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

class AttemptOwnershipMixin:
    def dispatch(self, request, *args, **kwargs):
        attempt = self.get_object()
        if attempt.student != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

class CourseOwnerRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if self.course.instructor != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
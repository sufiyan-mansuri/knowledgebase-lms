from django.core.exceptions import PermissionDenied
from enrollments.models import Enrollment
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

class InstructorRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        user = request.user

        if user.is_superuser:
            return super().dispatch(request, *args, **kwargs)

        if user.groups.filter(name='Instructors').exists():
            return super().dispatch(request, *args, **kwargs)

        raise PermissionDenied
    
class StudentRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        user = request.user

        if user.groups.filter(name='Students').exists():
            return super().dispatch(request, *args, **kwargs)
        
        raise PermissionDenied
    
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
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)

        if self.course.instructor != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
    
class NeverCacheMixin:
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
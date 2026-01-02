from django.core.exceptions import PermissionDenied

class InstructorRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        user = request.user

        print(user.groups.filter(name='instructor').exists())
        if not user.is_authenticated:
            raise PermissionDenied
        
        if not (user.is_superuser or user.groups.filter(name='Instructors').exists()):
            raise PermissionDenied
        
        return super().dispatch(request, *args, **kwargs)
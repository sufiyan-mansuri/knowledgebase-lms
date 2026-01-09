from django.http import HttpResponse
from django.shortcuts import redirect
from functools import wraps
from django.core.exceptions import PermissionDenied

def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper_func(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')

            if request.user.is_superuser:
                return wrapper_func

            user_groups = request.user.groups.values_list('name', flat=True)

            for role in user_groups:
                if role in allowed_roles:
                    return view_func(request, *args, **kwargs)
            
            raise PermissionDenied
            
        return wrapper_func
    return decorator
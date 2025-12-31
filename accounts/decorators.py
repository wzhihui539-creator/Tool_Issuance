from functools import wraps
from django.http import HttpResponseForbidden
from .utils import has_role

def role_required(role_name: str):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if has_role(request.user, role_name):
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden("403 Forbidden")
        return _wrapped
    return decorator
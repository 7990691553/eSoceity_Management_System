from functools import wraps
from django.core.exceptions import PermissionDenied
from django.contrib.auth.views import redirect_to_login


def role_required(*allowed_roles):
    """
    Usage:
        @role_required("security", "chairman", "super_admin")
    Superuser always allowed.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect_to_login(request.get_full_path())

            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            if getattr(request.user, "role", None) not in allowed_roles:
                raise PermissionDenied

            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator
from django.http import HttpResponseForbidden


def require_login(func):
    def decorator(request, *args, **kwargs):
        if not request.user.is_authenticated():
            return HttpResponseForbidden()
        return func(request, *args, **kwargs)
    return decorator

from django.http import HttpResponseForbidden
from flat_api_django.exceptions import UnauthorizedError


def require_login(func):
    def decorator(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        return func(request, *args, **kwargs)

    return decorator


def none_if_unauthenticated(func):
    def decorator(self, info, *args, **kwargs):
        if not info.context.user.is_authenticated:
            return None
        return func(self, info, *args, **kwargs)

    return decorator


def raise_if_unauthenticated(func):
    def decorator(self, info, *args, **kwargs):
        if not info.context.user.is_authenticated:
            raise UnauthorizedError('Unauthorized')
        return func(self, info, *args, **kwargs)

    return decorator

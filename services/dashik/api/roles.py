import logging
from functools import wraps

from django.http import HttpRequest, HttpResponseForbidden


logger = logging.getLogger(__name__)


def allowed_roles(*roles):
    def decorator(func):
        @wraps(func)
        def wrapper(request: HttpRequest, *args, **kwargs):
            user_roles = request.headers.get('X-Forwarded-Groups', '').split(',')
            logger.error('User roles: %s', user_roles)
            if any(allowed_role in user_roles for allowed_role in roles):
                return func(request, *args, **kwargs)
            return HttpResponseForbidden('User not allowed!')
        return wrapper
    return decorator

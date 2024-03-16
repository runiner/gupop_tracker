import logging

from django.http import HttpResponse, HttpRequest

from .roles import allowed_roles

logger = logging.getLogger(__name__)


# TODO:
#  - add endpoint with amount earned today and how many popugs gets into negative today
#  - add endpoint with most expensive task in current period

@allowed_roles('popug_admin')
def daily_stats(request: HttpRequest) -> HttpResponse:
    if request.method == 'GET':
        return HttpResponse('Daily stat')
    else:
        raise NotImplementedError(f'not supported method {request.method}')


@allowed_roles('popug_admin')
def tasks_stats(request: HttpRequest) -> HttpResponse:
    if request.method == 'GET':
        return HttpResponse('Task stats')
    else:
        raise NotImplementedError(f'not supported method {request.method}')

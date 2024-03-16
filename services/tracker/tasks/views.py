import logging

from django.http import HttpResponse, HttpRequest

from .roles import allowed_roles

logger = logging.getLogger(__name__)


def tasks(request: HttpRequest) -> HttpResponse:
    if request.method == 'GET':
        return HttpResponse('List all tasks')
    elif request.method == 'POST':
        return HttpResponse('Create new Task')
    else:
        raise NotImplementedError(f'not supported method {request.method}')


def task_close(request: HttpRequest, task_id: int) -> HttpResponse:
    if request.method == 'POST':
        # TODO: check user owns the task
        return HttpResponse(f'Close Task {task_id}')
    else:
        raise NotImplementedError(f'not supported method {request.method}')


def tasks_my(request: HttpRequest, task_id: int) -> HttpResponse:
    if request.method == 'GET':
        return HttpResponse(f'Info about my Task {task_id}')
    else:
        raise NotImplementedError(f'not supported method {request.method}')


@allowed_roles('popug_admin', 'popug_manager')
def tasks_shuffle(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        return HttpResponse(f'Shuffle tasks')
    else:
        raise NotImplementedError(f'not supported method {request.method}')

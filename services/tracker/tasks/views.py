import datetime
import json
import logging
import random

from django.db import transaction
from django.http import HttpResponse, HttpRequest

from .roles import allowed_roles
from . import models
from . import queue

logger = logging.getLogger(__name__)


@allowed_roles('popug_admin')
def tasks(request: HttpRequest) -> HttpResponse:
    if request.method == 'GET':
        tasks = models.Task.objects.all().values('task_id', 'title', 'status', 'owner__username')
        return HttpResponse(json.dumps(list(tasks)))
    elif request.method == 'POST':
        owner = models.User.objects.order_by('?').first()
        if not owner:
            return HttpResponse('No users found', status=500)
        with transaction.atomic():
            task = models.Task.objects.create(
                owner=owner,
                title=request.POST['title'],
                description=request.POST.get('description', ''),
            )
            queue.get_client().publish_message(
                routing_key='TaskCreated',
                message={
                    'name': 'TaskCreated',
                    'params': {
                        'task_id': task.task_id,
                        'title': task.title,
                        'description': task.description,
                        'user_id': task.owner.user_id,
                    }
                }
            )
        msg = f'New task {task.task_id} created for user {owner.username}'
        logger.info(msg)
        return HttpResponse(msg)
    else:
        raise NotImplementedError(f'not supported method {request.method}')


def task_close(request: HttpRequest, task_id: int) -> HttpResponse:
    if request.method == 'POST':
        with transaction.atomic():
            try:
                task = models.Task.objects.get(
                    task_id=task_id,
                    owner__username=request.headers['X-Forwarded-User'],
                    status=models.TaskStatus.NEW,
                )
            except models.Task.DoesNotExist:
                return HttpResponse('Task not found or not owned', status=404)
            task.status = models.TaskStatus.CLOSED
            task.save()
            queue.get_client().publish_message(
                routing_key='TaskCompleted',
                message={
                    'name': 'TaskCompleted',
                    'params': {
                        'task_id': task.task_id,
                        'title': task.title,
                        'owner_id': task.owner_id,
                        'datetime': datetime.datetime.now().isoformat()
                    }
                }
            )

        return HttpResponse(f'Closed Task {task_id}')
    else:
        raise NotImplementedError(f'not supported method {request.method}')


def tasks_my(request: HttpRequest) -> HttpResponse:
    if request.method == 'GET':
        tasks = models.Task.objects.filter(owner__username=request.headers['X-Forwarded-User']).values('task_id', 'title', 'status')
        return HttpResponse(json.dumps(list(tasks)))
    else:
        raise NotImplementedError(f'not supported method {request.method}')


@allowed_roles('popug_admin', 'popug_manager')
def tasks_shuffle(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        developer_ids = models.User.objects.filter(roles='popug_developer').values_list('user_id', flat=True)
        if not developer_ids:
            return HttpResponse('No developers found', status=500)
        with transaction.atomic():
            tasks = models.Task.objects.filter(status=models.TaskStatus.NEW)
            new_assignments = []
            for task in tasks:
                task.owner_id = random.choice(developer_ids)
                task.save()
                new_assignments.append({
                    'task_id': task.task_id,
                    'user_id': task.owner_id,
                })
            queue.get_client().publish_message(
                routing_key='TasksReassigned',
                message={
                    'name': 'TasksReassigned',
                    'params': {
                        'reassigned': new_assignments,
                        'datetime': datetime.datetime.now().isoformat(),
                    }
                }
            )
        return HttpResponse(f'Tasks shuffled successfully!')
    else:
        raise NotImplementedError(f'not supported method {request.method}')

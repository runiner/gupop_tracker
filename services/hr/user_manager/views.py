import logging

from django.forms.models import model_to_dict
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from . import models, queue
from .keycloak import create_user
from .roles import allowed_roles

logger = logging.getLogger(__name__)


@allowed_roles('popug_admin')
def users(request: HttpRequest) -> HttpResponse:
    if request.method == 'GET':
        users = models.User.objects.all()
        return render(request, 'user_manager/list_users.html', {'users': users})
    elif request.method == 'POST':
        new_user_id = create_user(
            email=request.POST['email'],
            username=request.POST['username'],
            password=request.POST['password'],
            roles=[request.POST['role']],
        )
        new_obj, _ = models.User.objects.get_or_create(
            email=request.POST['email'],
            username=request.POST['username'],
            roles=str(request.POST['role']),
        )
        queue.get_client().publish_message(
            routing_key='NewUser',
            message={
                'name': 'UserUpdated',
                'params': model_to_dict(new_obj),
            }
        )
        logger.info(f'New user created: {new_user_id}/{new_obj.user_id}')

        return HttpResponseRedirect(reverse('users'))
    else:
        raise NotImplementedError(f'not supported method {request.method}')


@allowed_roles('popug_admin')
def update_user(request: HttpRequest, user_id: int) -> HttpResponse:
    if request.method == 'GET':
        return HttpResponse(f'Data about User {user_id}')
    elif request.method == 'POST':
        return HttpResponse(f'User updated {user_id}')
    elif request.method == 'DELETE':
        return HttpResponse(f'User {user_id} deleted')
    else:
        raise NotImplementedError(f'not supported method {request.method}')

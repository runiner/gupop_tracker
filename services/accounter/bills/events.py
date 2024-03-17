import random
import datetime

from django.db import transaction
from pydantic import BaseModel, ConfigDict

from . import models
from .queue import get_client

rabbit_client = get_client()


class Event(BaseModel):
    name: str
    params: dict


class UserUpdated(BaseModel):
    model_config = ConfigDict(extra='allow')

    user_id: int
    email: str
    username: str
    roles: str


@rabbit_client.add_handler('UserUpdated')
def on_user_updated(message):
    event = Event.model_validate(message)
    user_updated = UserUpdated.model_validate(event.params)

    models.User.objects.update_or_create(
        user_id=user_updated.user_id,
        defaults={
            'username': user_updated.username,
            'roles': user_updated.roles,
        },
    )


class TaskCreated(BaseModel):
    model_config = ConfigDict(extra='allow')

    task_id: int
    title: str
    description: str
    user_id: int


@rabbit_client.add_handler('TaskCreated')
def on_task_created(message):
    event = Event.model_validate(message)
    task_created = TaskCreated.model_validate(event.params)
    assign_cost = random.randint(10, 20)
    complete_cost = random.randint(20, 40)

    with transaction.atomic():
        models.Task.objects.create(
            task_id=task_created.task_id,
            title=task_created.title,
            assign_cost=assign_cost,
            complete_cost=complete_cost,
        )
        user = models.User.objects.get(user_id=task_created.user_id)
        if not hasattr(user, 'account'):
            models.Account.objects.create(user=user)
        # assigning
        account = models.Account.objects.select_for_update().get(pk=user.account.pk)
        tr = models.Transaction.objects.create(
            account=account,
            amount=assign_cost,
            description=f'Assign cost for task {task_created.task_id}/"{task_created.title}"',
            direction=-1,
        )
        account.balance -= assign_cost
        account.save()

        rabbit_client.publish_message(
            routing_key='BalanceUpdated',
            message={
                'name': 'BalanceUpdated',
                'params': {
                    'user_id': user.user_id,
                    'change': -assign_cost,
                    'new_balance': account.balance,
                    'description': tr.description,
                }
            }
        )


class TaskCompleted(BaseModel):
    model_config = ConfigDict(extra='allow')

    task_id: int
    title: str
    owner_id: int
    datetime: str


@rabbit_client.add_handler('TaskCompleted')
def on_task_completed(message):
    event = Event.model_validate(message)
    task_completed = TaskCompleted.model_validate(event.params)

    with transaction.atomic():
        task = models.Task.objects.get(task_id=task_completed.task_id)
        complete_cost = task.complete_cost
        account = models.Account.objects.select_for_update().get(owner_id=task_completed.owner_id)
        tr = models.Transaction.objects.create(
            account=account,
            amount=complete_cost,
            description=f'Complete cost for task {task_completed.task_id}/"{task_completed.title}"',
            direction=1,
        )
        account.balance += complete_cost
        account.save()

        rabbit_client.publish_message(
            routing_key='BalanceUpdated',
            message={
                'name': 'BalanceUpdated',
                'params': {
                    'user_id': task_completed.owner_id,
                    'change': complete_cost,
                    'new_balance': account.balance,
                    'description': tr.description,
                }
            }
        )


class TaskNewAssignment(BaseModel):
    model_config = ConfigDict(extra='allow')

    task_id: int
    user_id: int


class TasksReassigned(BaseModel):
    model_config = ConfigDict(extra='allow')

    reassigned: list[TaskNewAssignment]
    datetime: datetime.datetime


@rabbit_client.add_handler('TasksReassigned')
def on_tasks_reassigned(message):
    event = Event.model_validate(message)
    tasks_reassigned = TasksReassigned.model_validate(event.params)

    with transaction.atomic():
        for new_assignment in tasks_reassigned.reassigned:
            task = models.Task.objects.get(task_id=new_assignment.task_id)
            new_account = models.Account.objects.select_for_update().get(owner_id=new_assignment.user_id)
            tr = models.Transaction.objects.create(
                account=new_account,
                amount=task.assign_cost,
                description=f'Assign cost for task {task.task_id}/"{task.title}"',
                direction=-1,
            )
            new_account.balance -= task.assign_cost
            new_account.save()
            rabbit_client.publish_message(
                routing_key='BalanceUpdated',
                message={
                    'name': 'BalanceUpdated',
                    'params': {
                        'user_id': task.owner_id,
                        'change': -task.assign_cost,
                        'new_balance': new_account.balance,
                        'description': tr.description,
                    }
                }
            )

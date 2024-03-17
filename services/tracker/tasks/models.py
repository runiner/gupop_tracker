from django.db import models


class User(models.Model):
    user_id = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=50, unique=True, null=False, blank=False)
    roles = models.CharField(max_length=1200, null=False)


class TaskStatus(models.Choices):
    NEW = 'NEW'
    CLOSED = 'CLOSED'


class Task(models.Model):
    task_id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=250, null=False, blank=False)
    description = models.TextField(null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=TaskStatus.choices, default=TaskStatus.NEW)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
